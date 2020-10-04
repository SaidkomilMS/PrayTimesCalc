from datetime import date, timedelta
import math

def mytitle(st):
	return st[0].upper() + st[1:]

def tomorrow_date():
	return date.today() + timedelta(days=1)

sin = lambda x: math.sin(math.radians(x))
cos = lambda x: math.cos(math.radians(x))
tan = lambda x: math.tan(math.radians(x))
asin = lambda x: math.degrees(math.asin(x))
acos = lambda x: math.degrees(math.acos(x))
atan = lambda x: math.degrees(math.atan(x))
acot = lambda x: math.degrees(math.atan(1.0/x))
atan2 = lambda x, y: math.degrees(math.atan2(x, y))
