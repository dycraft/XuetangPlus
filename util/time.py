import time

#时间戳 -> 当地时间字符串
def stamp2localstr(stamp):
    local = time.localtime(stamp)
    return time.strftime('%Y-%m-%d %H:%M',local)

def current_stamp():
    return time.time()