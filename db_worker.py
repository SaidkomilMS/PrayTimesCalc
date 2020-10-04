import sqlite3
from location import Location

db = 'db.db'
connect = sqlite3.connect

def is_not_in_db(user_id):
	with connect(db) as connection:
		cursor = connection.cursor()
		result = cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
		return not bool(len(result))

def add_user(user_id):
	with connect(db) as connection:
		cursor = connection.cursor()
		data = (user_id, )
		cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", data)
		cursor.execute("INSERT INTO `locations` (`user_id`) VALUES (?)", data)
		cursor.execute("INSERT INTO `calc_method` (`user_id`) VALUES (?)", data)
		cursor.execute("INSERT INTO `asr_mode` (`user_id`) VALUES (?)", data)
		cursor.execute("INSERT INTO `time_zones` (`user_id`) VALUES (?)", data)

def save_location(user_id, location):
	with connect(db) as connection:
		cursor = connection.cursor()
		cursor.execute(
			"UPDATE `locations` SET `latitude` = ?, `longitude` = ? WHERE `user_id` = ?",
			(location.latitude, location.longitude, user_id)
		)

def save_timezone(user_id, tz_info):
	with connect(db) as connection:
		cursor = connection.cursor()
		cursor.execute(
			"UPDATE `time_zones` SET `tz_info` = ? WHERE `user_id` = ?",
			(tz_info, user_id)
		)

def save_calc_method(user_id, calc_method):
	with connect(db) as connection:
		cursor = connection.cursor()
		cursor.execute(
			"UPDATE `calc_method` SET `method` = ? WHERE `user_id` = ?",
			(calc_method, user_id)
		)

def save_asr_mode(mode):
	with connect(db) as connection:
		cursor = connection.cursor()
		cursor.execute(
			"UPDATE `asr_mode` SET `hanafi` = ? WHERE `user_id` = ?",
			(mode, user_id)
		)

def get_location(user_id):
	with connect(db)as connection:
		cursor = connection.cursor()
		result = cursor.execute("SELECT `latitude`,`longitude` FROM `locations` WHERE `user_id` = ?", (user_id, )).fetchone()
		location = Location(result[0], result[1])
		return location

def get_users():
	with connect(db) as connection:
		cursor = connection.cursor()
		results = cursor.execute("SELECT `user_id` FROM `users`").fetchall()
		if len(results) == 0:
			return []
		for r in results:
			yield r[0]

def get_timezone(user_id):
	with connect(db) as connection:
		cursor = connection.cursor()
		result = cursor.execute("SELECT `tz_info` FROM `time_zones` WHERE `user_id` = ?", (user_id, )).fetchone()
		return int(result[0])
