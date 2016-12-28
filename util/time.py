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

def date_today():
    now_stamp = time.time()
    today_stamp = utcstr_date_to_stamp(stamp_to_utcstr_date(now_stamp))
    return datetime.datetime.fromtimestamp(today_stamp)

def stamp_to_utcstr_date(stamp):
    return datetime.datetime.fromtimestamp(stamp).strftime('%Y-%m-%d')

def utcstr_date_to_stamp(utcstr):
    return datetime.datetime.strptime(utcstr, '%Y-%m-%d').timestamp()
