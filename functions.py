import pandas as pd
import math



#Ignore buggy warning from numpy
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

#FINDING DELIVERY COSTS
def find_delivery(json):
    delivery_costs = {}

    for index, row in json.iterrows():
        if row['warehouse_name'] in delivery_costs.keys():
            pass
        else:
            quantity = 0
            for product in row['products']:
                quantity += product['quantity']
            delivery_costs[row['warehouse_name']] = (row['highway_cost'] * -1) / quantity
    return delivery_costs



#CREATING TABLE FOR TRADES
def create_trades_mean(json, delivery_cost):
    trades_mean = pd.DataFrame({'product': [], 'quantity': [], 'income': [], 'expenses': [], 'profit': []})
    for index, row in json.iterrows():
        for product in row['products']:
            if product['product'] in trades_mean['product'].unique():
                trade_row = trades_mean.index[trades_mean['product'] == product['product']][0]
                trades_mean.at[trade_row, 'quantity'] = trades_mean.iloc[trade_row]['quantity'] + product['quantity']
                trades_mean.at[trade_row, 'income'] = trades_mean.iloc[trade_row]['income'] + product['price']*product['quantity']
                trades_mean.at[trade_row, 'expenses'] = trades_mean.iloc[trade_row]['expenses'] + delivery_cost[row['warehouse_name']]*product['quantity']
                trades_mean.at[trade_row, 'profit'] = trades_mean.iloc[trade_row]['income'] - trades_mean.iloc[trade_row]['expenses']
            else:
                new_row = pd.DataFrame({'product': [product['product']],
                                                     'quantity': [product['quantity']],
                                                     'income': [product['price']*product['quantity']],
                                                     'expenses': [delivery_cost[row['warehouse_name']]*product['quantity']],
                                                     'profit': [product['price']*product['quantity'] - delivery_cost[row['warehouse_name']]*product['quantity']]})
                trades_mean = pd.concat([trades_mean, new_row], ignore_index=True)



    return trades_mean


#TABLE FOR ORDER PROFITS
def order_profit(json):
    table_profit = pd.DataFrame({'order_id': [], 'order_profit': []})
    for index, row in json.iterrows():
        profit = 0
        for product in row['products']:
            profit += product['price']*product['quantity']
        profit += row['highway_cost']
        new_row = pd.DataFrame({'order_id': [str(row['order_id'])],
                                'order_profit': [profit]})
        table_profit = pd.concat([table_profit, new_row], ignore_index=True)
    mean_profit = table_profit['order_profit'].mean()

    return table_profit, mean_profit


def abc_helper(percent):
    if percent <= 70:
        return 'A'
    elif percent <= 90:
        return 'B'
    else:
        return 'C'

def abc_analysis(json, delivery_cost):
    main_table = pd.DataFrame({'warehouse_name': [], 'product': [], 'quantity': [], 'profit': [],
                                'percent_profit_product_of_warehouse': [], 'accumulated_percent_profit_product_of_warehouse': []})
    main_dict = {}
    #First, creating all the warehouses and products
    for index, row in json.iterrows():
        #Creating new warehouse name in case it didn't exist before
        if row['warehouse_name']  not in main_dict.keys():
            main_dict[row['warehouse_name']] = {}
        for product in row['products']:
            if product['product'] in main_dict[row['warehouse_name']].keys():
                main_dict[row['warehouse_name']][product['product']]['quantity'] += product['quantity']
                main_dict[row['warehouse_name']][product['product']]['profit'] += product['quantity'] * (
                            product['price'] - delivery_cost[row['warehouse_name']])
            else:
                main_dict[row['warehouse_name']][product['product']]= {}
                main_dict[row['warehouse_name']][product['product']]['quantity'] = product['quantity']
                main_dict[row['warehouse_name']][product['product']]['profit'] = \
                    product['quantity']*(product['price']-delivery_cost[row['warehouse_name']])
                main_dict[row['warehouse_name']][product['product']]['percent_profit_product_of_warehouse'] = 0

    #Calculating percent profit
    for warehouse in main_dict.keys():
        total_profit = 0

        for product in main_dict[warehouse].keys():
            if main_dict[warehouse][product]['profit'] > 0:
                total_profit += main_dict[warehouse][product]['profit']
        for product in main_dict[warehouse].keys():
            if main_dict[warehouse][product]['profit'] < 0:
                main_dict[warehouse][product]['percent_profit_product_of_warehouse'] = 0
            else:
                main_dict[warehouse][product]['percent_profit_product_of_warehouse'] = \
                    math.floor(main_dict[warehouse][product]['profit'] * 10000 / total_profit) / 100


    #Creating table
    for warehouse in main_dict.keys():
        for product in main_dict[warehouse].keys():
            new_row = pd.DataFrame({'warehouse_name': [warehouse],
                                    'product': [product],
                                    'quantity': [main_dict[warehouse][product]['quantity']],
                                    'profit': [main_dict[warehouse][product]['profit']],
                                    'percent_profit_product_of_warehouse': [main_dict[warehouse][product]['percent_profit_product_of_warehouse']]})
            main_table = pd.concat([main_table, new_row], ignore_index=True)

    print('Задание 4')
    print(main_table)

    #Sorting the table
    main_table = main_table.sort_values(['warehouse_name', 'percent_profit_product_of_warehouse'], ascending=False)

    print('Задание 5')
    print(main_table)



    #Filling the percent column
    total_percent = 0
    cur_warehouse = ""

    for index, row in main_table.iterrows():
        if row['warehouse_name'] == cur_warehouse:
            total_percent += row['percent_profit_product_of_warehouse']
            main_table.at[index, 'accumulated_percent_profit_product_of_warehouse'] = total_percent
        else:
            total_percent = row['percent_profit_product_of_warehouse']
            cur_warehouse = row['warehouse_name']
            main_table.at[index, 'accumulated_percent_profit_product_of_warehouse'] = total_percent

    main_table = main_table.reset_index(drop=True)

    main_table['category'] = main_table[
        'accumulated_percent_profit_product_of_warehouse'].apply(abc_helper)

    print('Задание 6')
    print(main_table)


    #In case you need to watch it in excel file
    # main_table.to_excel('ABC_table.xlsx', encoding='utf-8-sig')
    return

