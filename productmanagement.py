import re
import sys
import csv, os
from pandas import DataFrame
import queue
import datetime


# Initializing the dictionaries and CSV for product, warehouse and catalog
print("Welcome to Product Inventory Management System")

# Initializing a queue for batch logging
queue = queue.Queue(maxsize=2)

product= {
    'productName': '',
    'sku': ''
}

warehouse = {
    'number': None,
    'stockLimit': None,
    'wAvailable' : None
}

warehouseCatalog = {
    'itemSKU' : None,
    'numberWarehouse': None,
    'quantity' : None
}

pdf = DataFrame(data=None, index=None, columns=['ID', 'PRODUCT_NAME', 'SKU'])
pdf.to_csv(r'..\backend-take-home\productinventory.csv', index=None, header=True)

wdf = DataFrame(data=None, index=None, columns=['ID', 'WAREHOUSE_NUMBER', 'STOCK_LIMIT', 'AVAILABILITY'])
wdf.to_csv(r'..\backend-take-home\warehouse.csv', index=None, header=True)

wcdf = DataFrame(data=None, index=None, columns=['ID', 'ITEM_SKU', 'WAREHOUSE_NUMBER', 'QUANTITY'])
wcdf.to_csv(r'..\backend-take-home\warehousecatalog.csv', index=None, header=True)

# Defining usage of commands
def usage():
    print('''Please enter a valid command. The following are the valid commands:
          ADD PRODUCT "PRODUCT NAME" SKU
          ADD WAREHOUSE WAREHOUSE# [STOCK_LIMIT]
          STOCK SKU WAREHOUSE# QTY
          UNSTOCK SKU WAREHOUSE# QTY
          LIST PRODUCTS
          LIST WAREHOUSES
          LIST WAREHOUSE WAREHOUSE#''')

# Check if the product with SKU already exists
def checksku(sku):
    skuPresent = False
    with open('productinventory.csv', 'rt') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[2] == sku:
                skuPresent = True
    return skuPresent


# Check the validity of arguments for ADD PRODUCT command
def checkaddvalidity(replArgs):
    processedArgs = []
    partialStr = ""
    lastIndex = 0
    isPartofName = False
    validCommand = False

    # Parsing the product name
    for i in range(len(replArgs)):
        if replArgs[i].count("\"") == 2:
            partialStr = replArgs[i].strip('\"')
            lastIndex = i
            break
        else:
            if re.search(r"\"", replArgs[i]) and isPartofName == False:
                partialStr = partialStr + " " + replArgs[i].strip('\"')
                isPartofName = True
                continue
            if isPartofName == True:
                partialStr = partialStr + " " + replArgs[i].strip('\"')
            if re.search(r"\"", replArgs[i]) and isPartofName == True:
                partialStr = partialStr + " " + replArgs[i].strip('\"')
                isPartofName = False
                lastIndex = i
                break

    processedArgs.append(partialStr.strip())

    # print("Value of last index: ", lastIndex)
    # print("# of args left: ", replArgs[lastIndex+1:])

    # check if the SKU is of the valid format
    if len(replArgs[lastIndex + 1:]) == 1:
        sku = replArgs[lastIndex + 1]
        # print("SKU:"+sku)
        skuregex = re.compile(r'[0-9A-Za-z]{8}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{12}')
        if re.fullmatch(skuregex, sku):
            processedArgs.append(sku)
            validCommand = True
    else:
        # print("Invalid number of arguments")
        validCommand = False
        processedArgs.append(replArgs[lastIndex + 1:])

    return validCommand, processedArgs


# Check if the warehouse already exists
def checkwarehouse(wNumber):
    warehousePresent = False
    with open('warehouse.csv', 'rt') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[1] == str(wNumber):
                warehousePresent = True
    return warehousePresent


# Check if the SKU of the product is valid
def isvalidsku(sku):
    skuregex = re.compile(r'[0-9A-Za-z]{8}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{12}')
    if re.fullmatch(skuregex, sku):
        return True
    else:
        return False


# Update the availabilty in the warehouse and the catalog to update the stocking of products
def updateavailabilitystock(warehouseCatalog):
    stock =0
    all_rows =[]
    with open('warehouse.csv', 'r') as stock:
        reader = csv.reader(stock, delimiter=',')

        # Adding to the catalog by stocking items in warehouses
        with open('inter_warehouse.csv', 'w', newline='') as newStock:
            writer = csv.writer(newStock, delimiter=',')
            for row in reader:
                if row[1] == str(warehouseCatalog['numberWarehouse']):

                    # If the availabilty of the warehouse is greater than the number of products stocked
                    if int(row[3]) >= int(warehouseCatalog['quantity']):
                        row[3] = str(int(row[3]) - int(warehouseCatalog['quantity']))
                        stock = int(warehouseCatalog['quantity'])
                        all_rows.append(row)
                        # writer.writerow(row)
                        # print("Row: ", row)
                        print("ALL ITEMS STOCKED")
                        print("ITEM {} ADDED TO WAREHOUSE {}".format(warehouseCatalog['itemSKU'], warehouseCatalog['numberWarehouse']))

                    # If the availabilty of the warehouse is lesser than the number of items to be stocked
                    else:
                        total = warehouseCatalog['quantity']
                        # extra = int(warehouseCatalog['quantity']) - int(row[3])
                        warehouseCatalog['quantity'] = row[3]
                        stock = int(row[3])
                        row[3] = 0
                        all_rows.append(row)
                        print("ALL ITEMS CANNOT BE STOCKED")
                        print("{} ITEMS STOCKED OUT OF {}".format(warehouseCatalog['quantity'], total))
                else:
                    # writer.writerow(row)
                    all_rows.append(row)
            writer.writerows(all_rows)
    os.remove('warehouse.csv')
    os.rename('inter_warehouse.csv', 'warehouse.csv')

    allcatalogrows = []
    foundrow = False
    with open('warehousecatalog.csv', 'r') as inputfile:
        reader = csv.reader(inputfile, delimiter=',')

        # Update the availabilty of the warehouse
        with open('inter_warehousecatalog.csv', 'w', newline='') as outputfile:
            writer = csv.writer(outputfile, delimiter=',')
            for row in reader:
                if row[1] == str(warehouseCatalog['itemSKU']) and row[2] == str(warehouseCatalog['numberWarehouse']):
                    row[3] = str(int(row[3])+ stock)
                    allcatalogrows.append(row)
                    foundrow = True
                else:
                    allcatalogrows.append(row)

            if foundrow ==False:
                allcatalogrows.append([0, warehouseCatalog['itemSKU'], warehouseCatalog['numberWarehouse'], stock])

            writer.writerows(allcatalogrows)

    os.remove('warehousecatalog.csv')
    os.rename('inter_warehousecatalog.csv', 'warehousecatalog.csv')


# Update the availabilty in the warehouse and the catalog to update the unstocking of products
def updateavailabilityunstock(warehouseCatalog):

    all_rows = []
    unstocked = 0
    with open('warehousecatalog.csv', 'r') as unstock:
        reader = csv.reader(unstock, delimiter=',')

        with open('inter_warehousecatalog.csv', 'w', newline='') as newUnstock:
            writer = csv.writer(newUnstock, delimiter=',')
            for row in reader:
                # print ("Row", row)
                if row[1] == str(warehouseCatalog['itemSKU']) and row[2] == str(warehouseCatalog['numberWarehouse']):

                    # If the number of products to be unstocked is lesser than the number of products in stock
                    if int(row[3]) >= int(warehouseCatalog['quantity']):
                        # print("Is it even trying unstocking?")
                        row[3] = str(int(row[3]) - int(warehouseCatalog['quantity']))
                        all_rows.append(row)
                        print("{} ITEMS UNSTOCKED FROM WAREHOUSE {}".format(warehouseCatalog['quantity'],
                                                                     warehouseCatalog['numberWarehouse']))
                        unstocked = int(warehouseCatalog['quantity'])

                    # If the number of products to be unstocked is greater than the number of products in stock
                    else:
                        total = warehouseCatalog['quantity']
                        # extra = int(warehouseCatalog['quantity']) - int(row[3])
                        warehouseCatalog['quantity'] = row[3]
                        unstocked = int(row[3])
                        row[3] = 0
                        all_rows.append(row)
                        print("{} ITEMS UNSTOCKED OUT OF {}".format(warehouseCatalog['quantity'], total))
                else:
                    # writer.writerow(row)
                    all_rows.append(row)
            writer.writerows(all_rows)
    os.remove('warehousecatalog.csv')
    os.rename('inter_warehousecatalog.csv', 'warehousecatalog.csv')

    allwarehouserows = []
    with open('warehouse.csv', 'r') as inputfile:
        reader = csv.reader(inputfile, delimiter=',')

        # Update the warehouse availability
        with open('inter_warehouse.csv', 'w', newline='') as outputfile:
            writer = csv.writer(outputfile, delimiter=',')
            for row in reader:
                if row[1] == str(warehouseCatalog['numberWarehouse']):
                    row[3] = str(int(row[3])+ unstocked)
                    allwarehouserows.append(row)
                else:
                    allwarehouserows.append(row)
            writer.writerows(allwarehouserows)

    os.remove('warehouse.csv')
    os.rename('inter_warehouse.csv', 'warehouse.csv')



# Pretty printing of data
def prettyprint(data):
    col_width = max(len(word) for row in data for word in row) + 2  # padding
    for row in data:
        print("".join(word.ljust(col_width) for word in row))

# start of REPL; Ctrl+Z to exit the REPL
while True:
    try:
        if queue.full(): # Logging in batches of 2
            with open('pmsoftware.log', 'a', newline='\n') as logfile:
                logfile.write(str(datetime.datetime.now().strftime("%m/%d/%Y %I:%M:%S"))+" \t"+ queue.get()+"\n")
                logfile.write(str(datetime.datetime.now().strftime("%m/%d/%Y %I:%M:%S"))+" \t"+ queue.get()+"\n")
        run = input("Enter the command:")
        # print("Here: ", type(run))

        queue.put(run)
        replArgs = run.split(" ")
        # noOfArgs = len(replArgs)
        # print(replArgs)

        if replArgs[0].upper() == "ADD":

            # Adding a product
            if replArgs[1].upper() == "PRODUCT":
                validcmd, pArgs = checkaddvalidity(replArgs[2:])
                # print("Result", validcmd, pArgs)
                if validcmd == True:
                    # print("Add the object")
                    product['productName'] = pArgs[0]
                    product['sku'] = pArgs[1]

                    skuPresent = checksku(product['sku'])

                    if skuPresent == True:
                        print("ERROR ADDING PRODUCT PRODUCT with SKU {} ALREADY EXISTS".format(product['sku']))
                    else:
                        with open('productinventory.csv', 'a') as f:
                            df = DataFrame([product])
                            df.to_csv(f, header=False)
                        print("PRODUCT {} ADDED".format(product['sku']))
                else:
                    print("Invalid number of arguments")
                    usage()

            # Adding a warehouse
            elif replArgs[1].upper() == "WAREHOUSE":
                # print("Adding a warehouse")
                argList = replArgs[2:]
                # print("List of args: ",argList)
                noOfArgs = len(argList)
                if argList[0].isnumeric() and 0<noOfArgs<3:
                    warehouse['number'] = int(argList[0])
                    if noOfArgs == 1:
                        warehouse['stockLimit'] = sys.maxsize
                        warehouse['wAvailable'] = sys.maxsize
                    else:
                        if argList[1].isnumeric():
                            warehouse['stockLimit'] = int(argList[1])
                            warehouse['wAvailable'] = int(argList[1])

                    warehousePresent = checkwarehouse(warehouse['number'])
                    # print(warehouse, warehousePresent)
                    if warehousePresent:
                        print("ERROR ADDING WAREHOUSE WAREHOUSE NUMBER {} ALREADY EXISTS".format(warehouse['number']))
                    else:
                        with open('warehouse.csv', 'a') as f:
                            df = DataFrame([warehouse])
                            df.to_csv(f, header=False)
                        print("WAREHOUSE {} ADDED".format(warehouse['number']))
                else:
                    print("Invalid arguments/Invalid number of arguments")
                    usage()
            else:
                usage()

        # Stock items into warehouse
        elif replArgs[0].upper() == "STOCK":
            # print("Stocking up")
            if len(replArgs) ==4:
                validSKU = isvalidsku(replArgs[1]) & checksku(replArgs[1])
                validWarehouse = replArgs[2].isnumeric() & checkwarehouse(replArgs[2])
                if validSKU and validWarehouse and replArgs[3].isnumeric():
                    warehouseCatalog['itemSKU'] = replArgs[1]
                    warehouseCatalog['numberWarehouse'] = replArgs[2]
                    warehouseCatalog['quantity'] = replArgs[3]
                    updateavailabilitystock(warehouseCatalog)
                elif validSKU == False and validWarehouse == False:
                    print("PRODUCT AND WAREHOUSE DO NOT EXIST")
                elif validSKU ==False:
                    print("PRODUCT DOES NOT EXIST")
                elif validWarehouse ==False:
                    print("WAREHOUSE DOES NOT EXIST")
                else:
                    print("Invalid arguments")
                    usage()
            else:
                print("Invalid number of arguments")
                usage()

        # Unstock items from warehouse
        elif replArgs[0].upper() == "UNSTOCK":
            if len(replArgs) ==4:
                validSKU = isvalidsku(replArgs[1]) & checksku(replArgs[1])
                validWarehouse = replArgs[2].isnumeric() & checkwarehouse(replArgs[2])
                if validSKU and validWarehouse and replArgs[3].isnumeric():
                    # print("Unstocking items")
                    warehouseCatalog['itemSKU'] = replArgs[1]
                    warehouseCatalog['numberWarehouse'] = replArgs[2]
                    warehouseCatalog['quantity'] = replArgs[3]
                    updateavailabilityunstock(warehouseCatalog)

                elif validSKU == False and validWarehouse == False:
                    print("PRODUCT AND WAREHOUSE DO NOT EXIST")
                elif validSKU == False:
                    print("PRODUCT DOES NOT EXIST")
                elif validWarehouse == False:
                    print("WAREHOUSE DOES NOT EXIST")
                else:
                    print("Invalid arguments")
                    usage()
            else:
                print("Invalid number of arguments")
                usage()

        elif replArgs[0].upper() == "LIST" and len(replArgs)>1:

            # Listing the products
            pInventory =[]
            if replArgs[1].upper() == "PRODUCTS" and len(replArgs) == 2:
                with open('productinventory.csv', 'rt') as f:
                    reader = csv.reader(f, delimiter=',')
                    for row in reader:
                        pInventory.append([row[1], row[2]])
                prettyprint(pInventory)

            # Listing the items in the warehouse
            elif replArgs[1].upper() == "WAREHOUSE" and len(replArgs) == 3:
                productDict = {}
                if replArgs[2].isnumeric() and checkwarehouse(replArgs[2]):
                    catalog = [["ITEM NAME", "ITEM SKU", "QUANTITY"]]
                    with open('warehousecatalog.csv', 'rt') as f:
                        reader = csv.reader(f, delimiter=',')
                        for row in reader:
                            if replArgs[2] == row[2]:
                                catalog.append(['', row[1], row[3]])

                    if len(catalog) == 0:
                        print("WAREHOUSE {} IS EMPTY".format(replArgs[2]))
                    else:
                        with open('productinventory.csv', 'rt') as f:
                            reader = csv.reader(f, delimiter=',')
                            for row in reader:
                                productDict[row[2]] = row[1]

                        for row in catalog:
                            if row[1] in productDict:
                                row[0] = productDict[row[1]]
                            # row = row[::-1]

                        prettyprint(catalog)

                elif replArgs[2].isnumeric() == False:
                    print("Invalid arguments")
                    usage()
                elif replArgs[2].isnumeric() and checkwarehouse(replArgs[2]) ==False:
                    print("WAREHOUSE {} DOES NOT EXIST".format(replArgs[2]))

            # Listing the warehouses
            elif replArgs[1].upper() == "WAREHOUSES" and len(replArgs) == 2:
                warehouseList = []
                with open('warehouse.csv', 'rt') as f:
                    reader = csv.reader(f, delimiter=',')
                    for row in reader:
                        warehouseList.append([row[1]])
                prettyprint(warehouseList)

            else:
                print("Invalid arguments/Invalid number of arguments")
                usage()
        else:
            usage()

    # Handling of EOF
    except EOFError as e:
        print("Exiting the Product Inventory Management System")
        break





