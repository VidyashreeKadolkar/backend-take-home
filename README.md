# Rooms To Go - Take Home Assessment
Product Management Software is designed to manage the products in the inventory using simple commands.
It is used to add into/maintain products' inventory and a catalog that informs about the warehouse that has the product.

# Environment Setup
Product Management Software uses Python 3.6 with the following packages.

# Pre-requisites:
Install python 3.6
pip install pandas

# Components of the project
productmanagement.py
pmsoftware.log
productinventory.csv
warehouse.csv
warehousecatalog.csv

# Run code
python productmanagement.py

Once the code is run, a command line REPL is opened up, where you can provide one of the following commands:
1. ADD PRODUCT "PRODUCT NAME" SKU
2. ADD WAREHOUSE WAREHOUSE# [STOCK_LIMIT]
3. STOCK SKU WAREHOUSE# QTY
4. UNSTOCK SKU WAREHOUSE# QTY
5. LIST PRODUCTS
6. LIST WAREHOUSES
7. LIST WAREHOUSE WAREHOUSE#

to add a new product, add a new warehouse, stock items into a warehouse, unstock items from the warehouse, list products, list warehouses and list products in a warehouse respectively.

productinventory.csv stores all the products [PRODUCT_NAME, SKU]
warehouse.csv stores the warehouses' information [WAREHOUSE_NUMBER, STOCK_LIMIT, AVAILABILITY]
warehousecatalog.csv stores the quantity of each product stored in each warehouse [ITEM_SKU, WAREHOUSE_NUMBER, QUANTITY]

Commands are logged into pmsoftware.log in batches of 2

To exit from the product management software use Ctrl+Z (^Z) which is handled as EOF.

# Assumptions:
- The product name in ADD PRODUCT command is always enclosed in double-quotes (" ")
- If the stock limit is unspecified for a warehouse, the limit is set to sys.maxsize (9223372036854775807) value.

# Tests:
Since the product management software is REPL, testing can be done by running the code and issuing commands. A few commands are listed below:
```
- Check for unique warehouse:
> ADD WAREHOUSE 2 1000
> ADD WAREHOUSE 2

- Check for unique product SKU:
> ADD PRODUCT "Sofia Vegara 5 Piece Living Room Set" 38538505-0767-453f-89af-d11c809ebb3b
> ADD PRODUCT "BED" 38538505-0767-453f-89af-d11c809ebb3b

- Stock product into the warehouse and check it if exceeds the stock limit:
> STOCK 38538505-0767-453f-89af-d11c809ebb3b 2 1000
> STOCK 38538505-0767-453f-89af-d11c809ebb3b 2 1000

- Unstock product from the warehouse and check if the more of the same product can be unstocked
> UNSTOCK 38538505-0767-453f-89af-d11c809ebb3b 2 1000
> UNSTOCK 38538505-0767-453f-89af-d11c809ebb3b 2 1000

and so on.
```
