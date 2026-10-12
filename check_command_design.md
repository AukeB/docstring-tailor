# Design: `check` command

## Purpose

`check` reports structural problems in docstrings. It is separate from `format`,
which only reformats (wrapping and whitespace) and never changes a docstring's
meaning.

## High-level design

### Principles

- **Independent from `format`.** A failing check never blocks formatting, and
  formatting never depends on check results. This follows Ruff, where
  `ruff format` never runs lint rules.
- **Docstrings are not code.** A docstring problem is reported as a finding
  and fails `check`, but it never stops the Python code from running or being
  formatted. Pre-commit and CI can gate on `check`, while `format` ignores
  docstring problems.
- **Pre-commit first.** The package is primarily used as a pre-commit hook, so
  `check` must exit non-zero when it finds problems, and print results in a
  form that is easy to read in hook output.

### Rule system

Rules are grouped by category, similar to Ruff and ty:

| Prefix | Scope |
|--------|-------|
| `A` | General rules that apply to all styles (e.g. PEP 257 rules). |
| `G` | Google-style rules. |
| `N` | NumPy-style rules. |
| `S` | Sphinx-style rules. |
| `E` | Epydoc-style rules. |

Rule codes are a prefix plus a three-digit number, for example `A001` or
`G001`. This follows Ruff:

- Each prefix numbers its rules independently, so `G001` and `N001` have no
  relation to each other.
- Within a prefix, the hundreds digit groups rules by topic. The topic bands
  are decided together for each style, as described under Rule stability.

Each rule carries a boolean stating whether it is fixable. This flag is defined
per rule when the rule is created. Fixes are out of scope for the first version.

#### Selection and ignoring

Rules are selected and ignored in config, similar to Ruff, using `select` and
`ignore` lists. Users can name a full code (`G001`) or a prefix (`G`).

```toml
[tool.docstring_tailor]
style = "google"
select = ["A", "G"]
ignore = ["G001"]
```

- **Default selection.** If `select` is not set, `check` runs the `A` rules and
  the rules of the configured style.
- **Precedence.** When both lists match a rule, the more specific entry wins.
  A full code beats a prefix. With `select = ["G"]` and `ignore = ["G001"]`,
  every `G` rule runs except `G001`. Otherwise `ignore` wins over `select`
  when both name the same level.
- **CLI flags.** `check` also accepts `--select` and `--ignore`, with the same
  meaning as the config keys. Flags take priority over config, as with
  `--line-length` and `--style`.
- **Prefixes.** Any prefix of a code is accepted, as in Ruff, so `G` selects
  every Google rule and `G00` selects `G001` to `G009`.
- **Unknown codes.** A code or prefix that matches no rule is an error, as in
  Ruff, and `check` exits non-zero before running any rule.
- **Other styles.** A selected code that belongs to a style other than the
  configured one, such as `select = ["N"]` with `style = "google"`, prints a
  warning and is not run. Running `check` for another style stays possible
  through `--style`, as described under Command interface.

#### Rule stability

Users put rule codes in config, so a code must never change meaning once it is
released. Rules are therefore not added one at a time as they come to mind.
Instead:

- The complete rule set is designed before implementation starts, for all
  styles, including the topic bands for each prefix.
- Each code is assigned once, in that design, and the design is reviewed as a
  whole.
- After release, a code is retired rather than reused. When a rule is removed
  or renamed, its old code keeps working as a deprecated alias, so existing
  configs do not break. Using the alias prints a deprecation warning. The alias
  is kept for at least one minor release, then removed.

### Command interface

- `check` takes the same options as `format` (paths, `--style`,
  `--exclude`), and reads the same config file.
- `style` from config is the input for both `check` and `format`. Running
  `check` for a style the code does not use is allowed. It will produce many
  errors, and configuring the right style is the user's responsibility.
- `--style` is required when it is not set in config, as with `format`.

### Exit codes and output

- `format` exits non-zero when a file cannot be read or parsed. Those files are
  skipped and reported. This is current behaviour and is kept on purpose: an
  unparseable file cannot be formatted, and exiting 0 would let a pre-commit
  hook pass silently. Docstring problems never affect `format`'s exit code.
- `check` exits non-zero when any selected rule reports a problem, or when a
  file cannot be read or parsed.
- A file that cannot be read or parsed is reported on stderr as an `error:`
  line, the same as `format`. It has no rule code, and it does not count as a
  finding. A docstring that the parser cannot handle is treated the same way:
  it is a file-level error for the file that contains it, not a finding.
- Each finding is printed as `path:line: CODE message`, in the style of
  `ruff check`.
- The run ends with a summary line, in the style of `_format_run_summary`:
  `Found N issues in M files.` when there are findings, or `All checks passed!`
  when there are none. Here N counts findings and M counts files that have at
  least one finding. Files with an `error:` line are not counted as checked.
- Line numbers point to the line on which the docstring starts. A docstring can
  span many lines, so the message should name the offending entry where it can.

## Implementation design

### Approach

- The check command parses each docstring with the existing parser, then runs
  the rules over the resulting IR. Rules never reparse the text.
- Parsers only produce data. Rule logic does not go into the parsers, so
  `format` is unaffected by checks, and the parsers don't grow a branch for
  every rule.
- Each rule is a class with its code, style, fixable flag, and a `check(ir)`
  method that returns findings. A registry keyed by style and category selects
  the rules to run, using `select` and `ignore`.
- Where a rule needs information the IR does not record, the parser records it
  as **IR metadata**: a small set of fields that describe how the docstring was
  written, kept apart from the content fields. Examples are whether the summary
  line fits on one line, and whether a type was written in brackets. Metadata is
  computed from the raw text before `cleandoc` runs, since `cleandoc` discards
  the original layout. The renderer ignores metadata, so `format` output does
  not change.

### TODO for MVP

- The `check` command with the same options as `format`.
- The rule system (categories, codes, fixable flag, select and ignore).
- One rule only, to validate the design end to end: `A001`, from PEP 257. The
  summary paragraph must end with a period (`A001`, provisional until the full
  rule set is designed). The rule works as follows:
  - It applies only when the first IR node is a `Paragraph`. A docstring that
    starts with a list, a code block, a section, or nothing at all gets no
    finding.
  - It checks the last line of that first paragraph, so a one-line and a
    multi-line summary are treated the same way. A multi-line summary is
    left to the later one-line rule.
  - Only a period counts. `?` and `!` are not accepted for now.
  - The rule needs no parser changes and no IR metadata. Metadata is
    introduced with a later rule.
- No fixes.

### TODO after MVP

- The full rule set for each style, which is the next step before any rule is
  implemented.
- **Exact line and column of each finding**, like Ruff, as an improvement after
  the MVP. Today the parser works on the docstring text after `cleandoc` has
  removed indentation, so line offsets change. Carrying offsets through that
  step and into the IR is needed before findings can point at the exact
  position.
- **Suppression comments**, like Ruff's `# noqa`, so a user can silence one
  finding where a docstring is a deliberate exception. The `Finding` structure
  should leave room for this.
- **Per-file ignores**, like Ruff's `per-file-ignores`, so a rule can be turned
  off for a set of files, such as tests.
- **Warning for an empty selection.** When `select` and `ignore` leave no rules
  to run, `check` prints a warning. Without it, the run would print
  `All checks passed!`, which is misleading.

## Implementation steps

Steps are split into two groups. **Changes** modify code that already exists,
so they carry the most risk. **Additions** only add new code, so `format` and
the existing tests are not affected by them.

### Changes

1. [ ] Add the `check` command to the CLI in `main.py`, reusing the option
   handling, path collection and error reporting of `format`, plus the
   `--select` and `--ignore` flags.
2. [ ] Extract the per-file loop of `format` into a helper that `check` can
   share, without changing what `format` prints or returns.
3. [ ] Add `select` and `ignore` to the config loading in `utils_file_system.py`.

### Additions

1. [ ] Rule base class with code, style, fixable flag and `check(ir)`, plus a
   registry keyed by style and category.
2. [ ] Select and ignore resolution: prefix and full-code matching, applied to
   the registry.
3. [ ] Checker module that parses each docstring with the existing parser and
   runs the selected rules over the IR, recording the docstring start line.
4. [ ] Rule `A001`: the last line of the leading summary paragraph ends with a
   period. Skipped when the first IR node is not a `Paragraph`.
5. [ ] Output and summary formatting in the `path:line: CODE message` style.
6. [ ] Tests for rule `A001` against fixtures, using the existing golden-file
   layout.
7. [ ] Tests for the `check` command: findings, exit codes, and that `format`
   still exits 0 when a check would fail.
8. [ ] README section for the `check` command, the `select` and `ignore`
   config keys, and the `--select` and `--ignore` flags.
9. [ ] Pre-commit hook entry for `check` in `.pre-commit-hooks.yaml`, alongside
   the existing `format` hook. The same file's comment shows the style argument
   as `args: ["style", "google"]`; it should read `args: ["--style", "google"]`.
