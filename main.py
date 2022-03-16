# import json
# import io
import pandas as pd
import functions

task_json = pd.read_json('trial_task.json')




#Task 1
delivery_cost = functions.find_delivery(task_json)
print('Задание 1')
print(delivery_cost)




#TASK 2
trades_mean = functions.create_trades_mean(task_json, delivery_cost)
print('Задание 2')
print(trades_mean)


#TASK 3
order_profit, mean_profit = functions.order_profit(task_json)
print('Задание 3 (среднее)')
print(mean_profit)
print('Задание 3 (таблица)')
print(order_profit)


#TASK 4-6
functions.abc_analysis(task_json, delivery_cost)
