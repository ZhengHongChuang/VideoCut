# import os 
# fn = "aaaa/videos/test.mp3"
# ext = os.path.splitext(fn)[1][1:]
# print(ext)
import re
text = "[1,00:00]   我的名字是 Video Cut"
# m = re.match(r"\[(\d+)", text.strip())
m = re.match(r"\[(\d+)", text.strip())  # 使用正则表达式匹配任务序号
print(m.groups()[0])