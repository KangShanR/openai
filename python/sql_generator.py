import requests
# generate sql

def generateSql(start, end, template):
    """Print the prime numbers from start 2 end in the argument number"""
    for i in range(start, end):
        print(template.format(str(i).zfill(2)))

sql_tpl = "hello {}"

generateSql(0, 100, sql_tpl)
