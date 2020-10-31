# from datetime import datetime
from datetime import datetime, timedelta
from dateutil.parser import parse, isoparse

my_date = datetime.now()
print(my_date)
first_date = my_date - timedelta(hours=1)
print(my_date.isoformat())
print(first_date.isoformat())

print(type(my_date))

start = "2020-10-asdf:49"

try:
    print(isoparse(start))
except Exception as e:
    print(e)
    print("nono")
