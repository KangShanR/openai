import os
import mysql.connector

# 定义配置字典
config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host':'localhost',
    'database': 'testdb',
    'raise_on_warnings': True
}

try:
    # 创建连接
    conn = mysql.connector.connect(**config)
    print("数据库连接成功！")
except mysql.connector.Error as err:
    print(f"连接失败: {err}")