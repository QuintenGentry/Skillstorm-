from support_api.obtainStocks import load_manifest
from pathlib import Path

if __name__ == "__main__":
    # obtain stocks and their validity
    stockAssignments = load_manifest(Path("data/restock_manifest.json"))

    # print valid stocks
    valid_stocks = stockAssignments[0]
    print(" --- Valid stocks: ---")
    for stock in valid_stocks:
        print(f"{stock}")

    # print invalid stocks
    print("\n --- Invalid stocks: ---")
    for stock in stockAssignments[1]:
        print(f"Sku: {stock["sku"]} with error of {stock["errors"]}")
        

    



