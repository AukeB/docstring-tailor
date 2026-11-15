def load_orders(path: str, currency: str, limit: int | None) -> list[dict]:
    """Loads orders from a CSV export and converts the amounts to one currency.

    Rows that cannot be parsed are skipped and logged, so one bad line never stops
    an import.

    Every row goes through these checks:
    - Surrounding whitespace is stripped from every column, so values copied from a
      spreadsheet compare equal to values typed by hand.
    - Amounts are converted with the exchange rate of the order date, not the rate
      of the day the import runs.
    - Orders that are dated in the future are dropped, because they usually come
      from a misconfigured clock on the till.

    The import itself runs in three steps:
    1. Read the file and detect its delimiter and encoding.
    2. Parse and check every row, collecting the rows that fail.
    3. Return the valid orders, sorted by order date.

    Args:
        path (str): Location of the CSV export, absolute or relative to the working
            directory.
        currency (str): ISO 4217 code that all amounts are converted to.
        limit (int | None): Maximum number of orders to return. None returns all
            orders.

    Returns:
        list[dict]: One dictionary per order, with the keys "id", "date" and
            "amount".

    Raises:
        FileNotFoundError: If no file exists at the given path.
        ValueError: If the currency code is unknown.

    Examples:
        Convert all orders to US dollars:

        >>> orders = load_orders("orders.csv", currency="USD", limit=None)
        >>> orders[0]["amount"]
        12.5

    Note:
        Exchange rates are cached for one day. Importing the same file twice on
        one day therefore gives identical amounts, even if the rates change in
        between.

    A nightly job that prints a short report uses it like this:

    ```
    orders = load_orders("exports/orders.csv", currency="USD", limit=None)
    total = sum(order["amount"] for order in orders if order["date"] >= start_of_month)
    print(f"{len(orders)} orders, {total:.2f} USD since {start_of_month:%d %B}")
    ```
    """
    raise NotImplementedError
