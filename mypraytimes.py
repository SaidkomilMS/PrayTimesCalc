import math
from math import floor
from datetime import date, time
from spec_file import sin, cos, tan, asin, acos, atan, acot, atan2

from db_worker import *

class PrayTimes:

	@staticmethod
	def load_calculators():
		user_ids = get_users()
		mydict = {}
		for k in user_ids:
			mydict[k] = PrayTimes(k)
		return mydict

	def __init__(self, user_id, gen_method = 'Karachi', asr_method='Hanafi'):
		self.gen_method = gen_method #For the future
		self.asr_method = asr_method #For the future
		self.user_id = user_id
		if is_not_in_db(user_id):
			add_user(user_id)

	def get_times(self, us_date=None):
		self.location = get_location(self.user_id)
		self.timezone = get_timezone(self.user_id)
		if not(us_date):
			self.date = self.julian(date.today()) - self.location.longitude / (15 * 24.0)
		else:
			self.date = self.julian(us_date) - self.location.longitude / (15 * 24.0)
		self.get_Sun_pos()
		self.zuhr_time = self.get_zuhr_time() # Getting time in float type
		self.sunrise_time = self.zuhr_time - self.t_func(0.833) # Getting time in float type
		self.shom_time = self.zuhr_time + self.t_func(0.833) # Getting time in float type
		self.fajr_time = self.zuhr_time - self.t_func(18) # Getting time in float type
		self.isha_time = self.zuhr_time + self.t_func(18) # Getting time in float type
		self.asr_time = self.zuhr_time + self.a_func(2) # Getting time in float type
		return {
			'fajr': self.make_time(self.fajr_time), #Making datetime.time object from float type of time
			'quyosh': self.make_time(self.sunrise_time), #Making datetime.time object from float type of time
			'zuhr': self.make_time(self.zuhr_time), #Making datetime.time object from float type of time
			'asr': self.make_time(self.asr_time), #Making datetime.time object from float type of time
			'mag\'rib': self.make_time(self.shom_time), #Making datetime.time object from float type of time
			'isha': self.make_time(self.isha_time) #Making datetime.time object from float type of time
		}

	def julian(self, date):
		if date.month <= 2:
			year = date.year - 1
			month = date.month + 12
		else:
			year = date.year
			month = date.month
		A = year // 100
		B = 2 - A + A // 4
		return floor(365.25 * (year + 4716)) + floor(30.6001 * (month + 1)) + date.day + B - 1524.5

	def get_Sun_pos(self):
		d = self.date - 2451545.0

		g = self.fixangle(357.529 + 0.98560028 * d)
		q = self.fixangle(280.459 + 0.98564736 * d)
		L = self.fixangle(q + 1.915 * sin(g) + 0.020 * sin(2*g))

		R = 1.00014 - 0.1671 * cos(g) - 0.00014 * cos(2*g)
		e = 23.439 - 0.00000036 * d
		RA = atan2(cos(e) * sin(L), cos(L)) / 15

		self.D = asin(sin(e) * sin(L))
		self.EqT = q/15 - self.fixhour(RA)

	def make_time(self, stime):
		stime = self.fixhour(stime + 0.5/60.0)
		hour = floor(stime)
		minute = int((stime-floor(stime))*60)
		if minute >= 60:
			minute -= 60
			hour += 1
		return time(hour=hour, minute=minute)

	def get_zuhr_time(self):
		return 12 + self.timezone - self.location.longitude/15 - self.EqT

	def a_func(self, t):
		return acos((sin(acot(t + tan(self.location.latitude - self.D))) - sin(self.location.latitude)*sin(self.D))/(cos(self.location.latitude) * cos(self.D)))/15

	def fixangle(self, angle): return self.fix(angle, 360.0)
	def fixhour(self, hour): return self.fix(hour, 24.0)

	def fix(self, a, mode):
		if math.isnan(a):
			return a
		a = a - mode * (math.floor(a / mode))
		return a + mode if a < 0 else a

	def t_func(self, a):
		return acos((-sin(a)-sin(self.location.latitude)*sin(self.D))/(cos(self.location.latitude) * cos(self.D))) / 15
