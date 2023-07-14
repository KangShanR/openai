import pandas as pd

# tb = pd.read_html("http://rate.bot.com.tw/xrt?Lang=zh-TW")
tb = pd.read_html("https://baidu.com")

print(tb[0])
