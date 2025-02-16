import pandas as pd

tb = pd.html.read_html("http://rate.bot.com.tw/xrt?Lang=zh-TW")

print(tb[0])
