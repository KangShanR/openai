import datetime
from mysql_connect import engine
import pandas as pd





rows = pd.read_sql("select * from crontab where data_state = \"VALID\";", engine)
for row in rows:
    if(row['cron_type'] == "DAILY"):
        today_str = datetime.date.today().strftime("%Y-%m-%d %H:%M:%S")
        logs =pd.read_sql("""
                            select * from cron_log where `name` = %s and data_state = \"VALID\" 
                            AND task_result = \"SUCCESS\" AND created_at >= %s
                        """,
                        engine,
                        params=(row['name'], today_str))
        if logs.size() == 0:
            print("There is no {} task excuted in {}".format(row['name'], today_str))

