import pandas as pd

def compare_excel(excel1, excel2):
    # Read Excel file
    df = pd.read_excel(excel1, engine='openpyxl')

    data = {}

    for index, row in df.iterrows():
        key = str(row['vender_id']) + '-' + str(row['receive_locale_id'])
        value = str(row['bill_count']) +':' + str(row['item_count'])
        data[key] = value

    store = pd.read_excel(excel2, engine='openpyxl')
    store_data = {}
    for index, row in store.iterrows():
        key = str(row['vender_id']) + '-' + str(row['store_locale_id'])
        value = str(row['order_count']) +':' + str(row['item_count'])
        store_data[key] = value

    for key, value in data.items():
        store_value = store_data.pop(key)
        if store_value != value:
            print("Not equals " + str(key) +",bofc value:"+ str(value) +", store value:"+ str(store_value))
        # else:
        #     print("Equals " + key + ",value:" + value)

    print('remain store data:' + str(store_data))



# compare excel data cell by cell
def compare_excel2(excel1, excel2):
    # Read Excel file
    df = pd.read_excel(excel1, engine='openpyxl')

    data = list()

    for index, row in df.iterrows():
        value = str(row['biz_id']).split(',')
        data.extend(value)

    store = pd.read_excel(excel2, engine='openpyxl')
    store_data = list()
    for index, row in store.iterrows():
        key = str(row['purchase_no'])
        print(key)
        store_data.append(key)
    
    print('------------')

    for value in data:
        if value in store_data:
            print(str(value) +" existed ")
        else:
            print(str(value) + " not existed")



compare_excel2('~/Downloads/msg.xlsx', '~/Downloads/bills.xlsx')
