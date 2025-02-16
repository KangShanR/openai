import datetime
from mysql_connect import query_datas, query_data





rows = query_datas("select * from crontab where data_state = \"VALID\";", None)
for row in rows:
    if(row[1] == "DAILY"):
        logs = query_datas("""
                           select * from cron_log where `name` = %s and data_state = \"VALID\" AND
                            task_result = \"SUCCESS\" AND created_at >= %s
                           """, (row[2], datetime.date.today().strftime("%Y-%m-%d %H:%M:%S")))
        for log in logs:
            print(log)

