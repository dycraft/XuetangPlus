import time
import datetime

#时间戳 -> 当地时间字符串
def stamp_to_localstr_minute(stamp):
    #turn ms to s
    stamp = int(int(stamp) / 1000)
    dt = datetime.datetime.fromtimestamp(stamp)
    dt += datetime.timedelta(hours=8)
    return dt.strftime('%Y-%m-%d %H:%M')

def stamp_to_localstr_date(stamp):
    #turn ms to s
    stamp = int(int(stamp) / 1000)
    dt = datetime.datetime.fromtimestamp(stamp)
    dt += datetime.timedelta(hours=8)
    return dt.strftime('%Y-%m-%d')

def current_stamp():
    return time.time()