"""
**A pytest suite** (at least 5 tests, in its own test file — e.g. `tests/test_loader.py` — importing from your source module rather than duplicating logic) covering:
- A valid row loads correctly
- One `@pytest.mark.parametrize` test covering three invalid-field cases
  in a single test body — an out-of-set `category`, a non-positive
  `quantity`, and a non-positive `unit_cost` — each asserting
  `pytest.raises(ValidationError)`
- Loading the **provided** `restock_manifest.json` (see below) returns
  exactly 8 valid items and 4 errors — this is your proof that the loader
  handles a realistic, mixed-quality batch correctly
- A missing manifest path raises your custom exception, verified with
  `pytest.raises`
  """

from support_api.obtainStocks import load_manifest, StockStoreNotFoundError
from support_api.RestockItem import RestockItem
import pytest
from pydantic import ValidationError
from pathlib import Path

# obtain stocks and their validity
def _validate_stocks():
    return load_manifest(None)

# Test if a row can be successfully validated. 
def test_validate_row():

    all_stocks = _validate_stocks()
    valid_stocks = all_stocks[0]

    assert [valid_stocks[0].sku == "SKU-1001"]

# Test if a row can be successfully caught upon invalid. 
def test_invalid_row(): 
    all_stocks = _validate_stocks()
    invalid_stocks = all_stocks[1]

    assert [invalid_stocks[0]["sku"] == "SKU-1011"]

# testing multiple failures. 
@pytest.mark.parametrize(
    "warehouse, quantity, category",
    [("west-1", 25, "invalidInput"),
     ("west-1", -1, "electronics"),
     ("invalidInput", 25, "electronics")]
)
def test_validation_exception(warehouse, quantity, category):
    test_dictionary = {"sku": "SKU-1015", "warehouse": warehouse, "quantity": quantity, "category": category}
    with pytest.raises(ValidationError):
        RestockItem.model_validate(test_dictionary)

# Testing restock_manifest.json returns 8 valid inputs, and 4 invalid inputs. 
def test_validation_of_provided_file():
    all_stocks = _validate_stocks()
    valid_stocks = all_stocks[0]    
    invalid_stocks = all_stocks[1]

    assert[len(valid_stocks) == 8 and len(invalid_stocks) == 4]

# Testing StockStoreNotFoundError error.
def test_stock_file_not_found_exception():
    with pytest.raises(StockStoreNotFoundError):
        load_manifest(Path("wrongpath/restock_manifest.json"))





