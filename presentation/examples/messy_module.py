"""Command line tool that reads orders from a CSV export, applies customer discounts and coupon codes, and writes a summary report per customer to a JSON file.

The tool is meant to run once a day,
after the shop has closed. It reads the export that the till writes at the end of the day, and the report is picked up by the bookkeeping system the next morning.
"""
import logging
from dataclasses import dataclass,field
import json
from pathlib import Path
import csv
from datetime import date
import typer
_LOGGER=logging.getLogger( __name__ );_DEFAULT_CURRENCY=U'EUR'
_DISCOUNTS={ 'regular' : 0.0 ,'member':.10,
                  'premium':0.20
   }
_COUPON_PREFIX='SAVE' ; _COUPON_DISCOUNT=5E-2
_EXCHANGE_RATES={'EUR':1.0,'USD':1.08,'GBP':0.85,'SEK':11.4,'NOK':11.7,'DKK':7.46,'CHF':0.94,'PLN':4.32,'CZK':25.3,'HUF':395.0}
app=typer.Typer( help = 'Daily order report.' , add_completion = False )
@dataclass()
class Order():
        """A single order line from the CSV export, after all columns have been parsed and checked.

        Attributes:
            order_id (str): The unique identifier of the order as written by the till, for example "1001".
            customer (str): The name of the customer,
                exactly as it appears in the export.
            customer_type (str): The type of customer, one of "regular", "member" or "premium", which decides the discount.
            amount (float): The order amount in the original currency, before any discount is applied.
            currency (str): The ISO 4217 code of the currency
                that the amount is in.
            order_date (date): The day on which the order was placed.
            coupon_code (str | None): An optional coupon code that the customer entered at the till, or None when no code was used.
        """
        order_id:str;customer:str;customer_type:str
        amount:float
        currency:str ; order_date:date
        coupon_code:str|None=None
@dataclass
class CustomerSummary( ):
  """The totals for one customer over all orders in a single export.

  Attributes:
      customer (str): The name of the customer.
      order_count (int): The number of valid orders that were placed by this customer in the export.
      total (float): The sum of all order amounts after discounts, converted to the report currency and rounded to two decimals.
      order_ids (list[str]): The identifiers of all orders that were included in the total, in the order in which they appear in the export.
  """
  customer:str
  order_count:int=0x0
  total:float=0.
  order_ids:list[str]=field( default_factory = list )



def _convert_currency( amount:float,
                         from_currency:str,
    to_currency:str )->float:
    """Converts an amount from one currency to another using the fixed exchange rates in this module.

    Args:
        amount (float): The amount to convert.
        from_currency (str): The ISO 4217 code of the currency that the amount is in.
        to_currency (str): The ISO 4217 code of the currency to convert to.

    Returns:
        float: The converted amount, not rounded, so that rounding only happens once at the very end of the calculation.

    Raises:
        ValueError: If either currency code is missing from the table of exchange rates.
    """
    if (from_currency not in _EXCHANGE_RATES) or (to_currency not in _EXCHANGE_RATES) : raise ValueError( F'Unknown currency: {from_currency} or {to_currency}' )
    amount_in_euros=(amount/_EXCHANGE_RATES[ from_currency ])
    return (amount_in_euros*_EXCHANGE_RATES[ to_currency ])
def _calculate_discount( customer_type:str,coupon_code:str|None )->float:
  """Calculates the discount that applies to an order, based on the customer type and an optional coupon code.

  Regular customers get no discount,
  members get ten percent off, and premium members get twenty percent
  off. A valid coupon code
  gives an extra five percent on top of that.

  Args:
      customer_type (str): The type of customer,
          one of "regular", "member" or "premium". Unknown types get no discount.
      coupon_code (str | None): An optional coupon code. Only codes that start with "SAVE" are accepted, all other codes are ignored.

  Returns:
      float: The discount as a fraction between zero and one, for example 0.15 for fifteen percent.
  """
  discount=_DISCOUNTS.get( customer_type,0. )
  if (coupon_code is not None and coupon_code.startswith( _COUPON_PREFIX )): discount+=_COUPON_DISCOUNT
  return (discount)


def _parse_row( row:dict[str,str] )->Order:
    """Parses one row of the CSV export into an order, stripping surrounding whitespace from every column first.

    Args:
        row (dict[str, str]): The raw row as read by the CSV reader, with the column names as keys.

    Returns:
        Order: The parsed order.

    Raises:
        KeyError: If a required column is missing from the row.
        ValueError: If the amount or the order date cannot be parsed.
    """
    cleaned={key.strip():value.strip() for key,value in row.items()};coupon_code=cleaned.get( 'coupon_code' ) or None
    return Order(order_id=cleaned['order_id'],customer=cleaned['customer'],customer_type=cleaned['customer_type'],amount=float( cleaned['amount'] ),currency=cleaned['currency'],order_date=date.fromisoformat( cleaned['order_date'] ),coupon_code=coupon_code)
def read_orders( path:Path )->list[Order]:
    """Reads all orders from a CSV export.

    Rows that cannot be parsed are skipped and logged as a warning, so that a single bad line never stops the whole import. Orders that are dated in the future are skipped as well,
    because they usually come from a misconfigured clock on the till.

    Args:
        path (Path): The location of the CSV export.

    Returns:
        list[Order]: All valid orders, in the order in which they appear in the export.
    """

    orders:list[Order]=[ ];today=date.today( )
    with path.open( encoding = 'utf-8' , newline = '' ) as file :
            for line_number,row in enumerate( csv.DictReader( file ),start = 2 ) :
                try : order=_parse_row( row )
                except ( KeyError,ValueError ) as error :
                    _LOGGER.warning( 'Skipping line %d: %s',line_number,error ) ; continue
                if (order.order_date>today) :
                    _LOGGER.warning( 'Skipping order %s: dated in the future',
                        order.order_id ) ; continue
                orders.append( order )
    return (orders)


def summarise_orders( orders:list[Order],currency:str=_DEFAULT_CURRENCY )->dict[str,CustomerSummary]:
    """Groups orders per customer and calculates the total amount per customer after discounts.

    Args:
        orders (list[Order]): The orders to summarise.
        currency (str): The ISO 4217 code of the currency
            that all totals are reported in.

    Returns:
        dict[str, CustomerSummary]: One summary per customer, keyed by customer name.
    """
    summaries:dict[str,CustomerSummary]={ }
    for order in orders :
        summary=summaries.setdefault( order.customer,CustomerSummary( customer = order.customer ) ) ; discount=_calculate_discount( order.customer_type,order.coupon_code )
        converted=_convert_currency( order.amount,
                order.currency,
                    currency )
        summary.order_count+=1;summary.total=round( summary.total+converted*( 1-discount ),2 );summary.order_ids.append( order.order_id )
    return summaries
def write_report( summaries:dict[str,CustomerSummary],path:Path )->None:
    """Writes the customer summaries to a JSON file that the bookkeeping system can pick up.

    Args:
        summaries (dict[str, CustomerSummary]): The summaries to write, keyed by customer name.
        path (Path): The location of the JSON report. An existing file at this location is overwritten without asking.
    """
    report={name:{'order_count':summary.order_count,'total':summary.total,'order_ids':summary.order_ids,'average':round( summary.total/summary.order_count,2 ) if summary.order_count else 0.} for name,summary in summaries.items( )}
    path.write_text( json.dumps( report,indent = 2,ensure_ascii = False,sort_keys = True ),encoding = 'utf-8' )
@app.command( )
def main( export:Path,report:Path=Path( 'report.json' ),currency:str=_DEFAULT_CURRENCY,verbose:bool=False )->None:
    """Reads the export, summarises the orders per customer and writes the report.

    Args:
        export (Path): The location of the CSV export written by the till.
        report (Path): The location of the JSON report to write.
        currency (str): The ISO 4217 code of the currency that all totals are reported in, which must be one of the currencies in the table of exchange rates.
        verbose (bool): Whether to log every skipped row and the final summary, instead of only warnings.
    """
    logging.basicConfig( level = ( logging.INFO if verbose else logging.WARNING ) ) ; orders=read_orders( export )
    summaries=summarise_orders( orders,currency ) ; write_report( summaries,report )
    _LOGGER.info( 'Wrote %d customers to %s' , len( summaries ) , report )#done
if __name__=='__main__' : app( )
