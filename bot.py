import logging

import requests
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext, CallbackQueryHandler

bot_token = '1048010701:AAHDXPobgHZmlyNVWn3Dg4z4aVbwrGH5TB8'
PRIVAT_EXCHANGE_API_URL = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'

logging.basicConfig()


def human_readable_ccy(ccy_obj):
	# USD-UAH: 24.15000/24.55000
	return "{}-{}: {}/{}".format(
		ccy_obj['ccy'], ccy_obj['base_ccy'], ccy_obj['buy'], ccy_obj['sale'])


def start(update, context: CallbackContext):
	msg = update.message
	context.bot.send_message(msg.chat_id, 'text', reply_markup=ReplyKeyboardMarkup(
		[
			[KeyboardButton('Exchange Rate')],
			[KeyboardButton('Hello')]
		]
	))


def exchange_rate(update, context):
	msg = update.message
	if msg.text == 'Exchange Rate':
		response = requests.get(PRIVAT_EXCHANGE_API_URL)
		# [{"ccy":"USD","base_ccy":"UAH","buy":"24.15000","sale":"24.55000"}, ...]
		list_ccy = response.json()
		list_ccy_human = list(map(human_readable_ccy, list_ccy))
		context.bot.send_message(msg.chat_id, '\n'.join(list_ccy_human), reply_markup=InlineKeyboardMarkup(
			[
				[InlineKeyboardButton('Update', callback_data='update')],
				[InlineKeyboardButton('Goto Privat24', url='https://privat24.ua')]
			]
		))
	elif msg.text == 'Hello':
		context.bot.send_message(msg.chat_id, 'Hello')


def update_exch_rates(update: Update, context):
	query = update.callback_query
	query.edit_message_text('Updating...')

	response = requests.get(PRIVAT_EXCHANGE_API_URL)
	list_ccy = response.json()
	list_ccy_human = list(map(human_readable_ccy, list_ccy))

	query.edit_message_text('\n'.join(list_ccy_human), reply_markup=InlineKeyboardMarkup(
		[
			[InlineKeyboardButton('Update', callback_data='update')],
			[InlineKeyboardButton('Goto Privat24', url='https://privat24.ua')]
		]
	))


def main():
	bot = Updater(bot_token, use_context=True)
	dp = bot.dispatcher

	dp.add_handler(CommandHandler('start', start))
	dp.add_handler(MessageHandler(Filters.text, exchange_rate))
	dp.add_handler(CallbackQueryHandler(update_exch_rates, pattern='update'))

	bot.start_polling()


if __name__ == '__main__':
	main()
