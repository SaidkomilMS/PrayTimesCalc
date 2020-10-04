from telegram import *
from telegram.ext import *
import logging
from config import *
from datetime import date, timedelta

# -------------My modules-----------------
from spec_file import mytitle, tomorrow_date
from mypraytimes import PrayTimes
import db_worker as db

# -----------Constantas--------------
LOCATION, TIMEZONE, RASSILKA = range(3)

# -----------------------Enable logging-----------------------
logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level=logging.INFO
)
logger = logging.getLogger(__name__)

# -----------------Creating gloabal variable-----------------
calculators = {}

# -----------Functions for handling messages-----------
def create_user(update: Update, context: CallbackContext):
	"""
		Is used for starting the registration.
		Creates the PrayTimes object which will calculate times.
		Just created PrayTimes object was saved in 'calculators' global variable
		with key that equals to users Telegram'id.
		And answers the user for the /start command and
		'Ro`yhatdan o`tish' text.
	"""
	global calculators
	user_json = update.message.from_user
	chat_id = user_json.id
	name = str()
	if user_json.last_name:
		name += user_json.last_name
	name += f' {user_json.first_name}'
	calculators[chat_id] = PrayTimes(chat_id)
	context.bot.send_message(
		chat_id=chat_id,
		text=(
			f'Assalomu alaykum, Hurmatli {name}!\n\n'
			'Botdan foydalanish uchun ro`yhatdan o`tishingiz zarur!\n'
			'Vaqtingiz bilan UTC orasidagi vaqt farqini jo`nating\n'
			'(O`zbekiston uchun +5)'
		),
	)
	return TIMEZONE

def set_timezone(update: Update, context: CallbackContext):
	"""
		Is used for saving the relation between UTC
		and users timezone. Saves the information to database by
		function from the db_worker.py file.
		And this function answers to user and asks for a location of user. 
	"""
	user_json = update.message.from_user
	chat_id = user_json.id
	tz_info = int(update.message.text)
	db.save_timezone(chat_id, tz_info)
	text = (
		'Endi manzilingizni jo`nating.'
	)
	keyboard = [[KeyboardButton('Manzilimni jo`natish', request_location=True)]]
	context.bot.send_message(
		chat_id= chat_id,
		text=text,
		reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
	)
	return LOCATION


def set_location(update: Update, context: CallbackContext):
	"""
		Saves the location  of user to the database.
		And sends the default settings info to user.
		Also function sends the keyboard contains two keys:
		  'Bugungi vaqtlar'
		  'Ertangi vaqtlar'
		Theese key helps users to faster send special messages.
	"""
	user_json = update.message.from_user
	chat_id = user_json.id
	location = update.message.location
	db.save_location(chat_id, location)
	keyboard = [['Bugungi vaqtlar'], ['Ertangi vaqtlar']]
	text = (
		'Boshlang`ich sozlamalar:\n'
		'<b>Hisoblash uslubi</b>: <em>Islomiy Fanlar Universiteti, Karachi</em>\n'
		'<b>Mazhab</b>: <em>Hanafiy (Asrga ta\'siri mavjud)</em>\n'
		'Birozdan so`ng bu sozlamalarni o`zgartirish imkoniyati yaratiladi.'
		' Yangiliklardan habardor bo`lib turish uchun botni bloklamang.'
	)
	context.bot.send_message(
		chat_id=chat_id,
		text=text,
		parse_mode=ParseMode.HTML,
		reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
	)
	return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
	"""
		Stops registration for users.
		And sends the special key 'Ro`yhatdan o`tish'
		which can start the regisration later.
	"""
	keyboard = [[KeyboardButton('Ro`yhatdan o`tish')]]
	context.bot.send_message(chat_id=update.effective_chat.id, text="Ro`yhatdan o`tish to`xtatildi",
		reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

def send_times(update: Update, context: CallbackContext):
	"""
		Answers to the special messages:
		 'Bugungi vaqtlar'
		 'Ertangi vaqtlar'
		For 'Bugungi vaqtlar' sends the pray times for today.
		For 'Ertangi vaqtlar' sends the pray times for tomorrow.
	"""
	global calculators
	user_json = update.message.from_user
	chat_id = user_json.id
	us_date = {'Ertangi vaqtlar': tomorrow_date}.get(update.message.text, date.today)()
	text = 'Namoz vaqtlari:\n\n'
	times = calculators[chat_id].get_times(us_date)
	for k, v in times.items():
		text += f'<b>{mytitle(k)}</b>: <em>{v.strftime("%H:%M")}</em>\n\n'
	context.bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)

# --------------------------------Main script--------------------------------

if __name__ == '__main__':
	# Updater object. To get updates from the telegram
	updater = Updater(TOKEN, use_context=True, workers=100)
	
	#Dispatcher object is used for right runnings of the functions
	dp = updater.dispatcher
	
	# --Loads calculators from the database--
	calculators = PrayTimes.load_calculators()

	# The Conversation between bot and user used for registration of the user
	registration = ConversationHandler(
		entry_points=[
			CommandHandler('start', create_user),
			MessageHandler(Filters.regex('^(Ro`yhatdan o`tish)$'), create_user)
		],
		states={
			LOCATION: [MessageHandler(Filters.location, set_location)],
			TIMEZONE: [MessageHandler(Filters.text, set_timezone)]
		},
		fallbacks=[
			CommandHandler('cancel', cancel)
		]
	)

	# -------------------------------Handler of the special messages-------------------------------
	times_handler = MessageHandler(Filters.regex('^(Bugungi vaqtlar|Ertangi vaqtlar)$'), send_times)

	# Adding handlers to the dispathcer info
	dp.add_handler(times_handler)
	dp.add_handler(registration)
	
	# Printing the messages that compilation has been successfully
	print('Start')
	
	updater.start_polling()
	updater.idle()