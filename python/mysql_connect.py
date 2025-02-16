import os
import mysql.connector

# 定义配置字典
config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host':'localhost',
    'database': 'testdb',
    'raise_on_warnings': True,
    'pool_name':"my_pool",
    "pool_size":5,
    "pool_reset_session": True 
}

# 创建连接池
pool =mysql.connector.pooling.MySQLConnectionPool(**config)


# 方法 1：查询多行数据
def query_datas(sql, values):
    conn = pool.get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, values)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

# 方法 1：查询单行数据
def query_data(sql, value):
    conn = pool.get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, value)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

# 方法 2：插入数据
def insert_data(sql, values):
    conn = pool.get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, values)
    conn.commit()
    cursor.close()
    conn.close()
