# test duration
# time math

from datetime import datetime
import time

time1 = datetime.today()#.time()
time.sleep(1)
time2 = datetime.today()#.time()

timestamp1 = str(time1.hour) + ':' + str(time1.minute) + ':' + str(time1.second)
timestamp2 = str(time2.hour) + ':' + str(time2.minute) + ':' + str(time2.second)
print('Time1: ' + timestamp1 + '')
print('Time2: ' + timestamp2 + '')


duration = (time2 - time1).seconds
#duration = datetime.combine(datetime.date.min, time2) - datetime.combine(datetime.date.min, time1)
print('Duration: ' + str(duration))