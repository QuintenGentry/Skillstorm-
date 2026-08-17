import json
from support_api.RestockItem import RestockItem
from support_api.config import AppSettings
from pathlib import Path
from pydantic import ValidationError

"""
**A defensive loader function**, `load_manifest(path) -> tuple[list[RestockItem], list[dict]]`
(or an equivalent shape of your choosing — document it if you deviate),
that:
- Reads a JSON file containing a list of item rows (plain dicts)
- Validates each row into a `RestockItem`
- Skips any row that fails validation and collects it into an error report
  instead of letting the whole batch crash on one bad row
- Raises your custom "not found" exception (not a bare `FileNotFoundError`)
  if the file doesn't exist
  """

class StockStoreError(Exception):
    """ base error """

class StockStoreNotFoundError(StockStoreError):
    """ Indicates if file is not obtained. """

class InvalidStockFormatError(StockStoreError):
    """ Indicates if file format is incorrect """








def load_manifest(path: Path | None = None) -> tuple[list[RestockItem], list[dict]]:
    # obtain path from AppSettings, or utilize input parameter. 
    resolved_path = path if path is not None else AppSettings().data_path

    print(resolved_path)
    
    raw_text = ""
    try:
        raw_text = resolved_path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise StockStoreNotFoundError(f"No file found at input location: {resolved_path}") from e


    stocks = []

    try:
        # loads: Converts a string (json format) into a python object. 
        stocks = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise InvalidStockFormatError(f"Input data from {resolved_path} is not in the desired format.") from e

    valid_stocks: list[RestockItem] = []
    invalid_stocks: list[dict[str, list[str]]] = []



    for stock in stocks:
        try:
            valid_stocks.append(RestockItem.model_validate(stock))
        except ValidationError as e:
            # loop through e, which represents the errors, and grabs the e['loc'] and e['msg'] from the error. 
            err_msgs = [f"{e['loc']} : {e['msg']}" for e in e.errors()]
            invalid_stocks.append({"sku": stock.get("sku", "no sku"), "errors": err_msgs})

    returnTuple: tuple[list[RestockItem], list[dict]] = valid_stocks, invalid_stocks



    return returnTuple

    

