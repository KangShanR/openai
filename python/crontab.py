import datetime
from mysql_connect import query_datas, engine
import pandas as pd





rows = pd.read_sql("select * from crontab where data_state = \"VALID\";", engine)
for row in rows:
    if(row[1] == "DAILY"):
        logs =pd.read_sql("""
                            select * from cron_log where `name` = %s and data_state = \"VALID\" 
                            AND task_result = \"SUCCESS\" AND created_at >= %s
                        """,
                        engine,
                        params=(row[2],datetime.date.today().strftime("%Y-%m-%d %H:%M:%S")))
        for log in logs:
            print(log)

