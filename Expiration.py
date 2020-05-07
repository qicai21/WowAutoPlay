import time

def checkByExpiredHash(_hash, how_long=15):
    """进行有效期检验,how_long为最大检验天数，默认向后检查15天，每小时为1个检验单元。
    """
    _t = int(time.time()/60/60)*60*60
    for i in range(24*how_long):
        if hash(time.localtime(_t)) == _hash:
            return True
        _t += 60*60

    # while current > expired, can't match
    # or reset expired_hash illegally, can't match either.
    return False


def createExpiredHash(expired_time):
    """Pls using time.mktime() to create a date param
        t = time.mktime((2020,5,15,10,30,0,-1,-1,-1))
        h = createExpiredHash(t)
    """
    return hash(time.localtime(expired_time))