from telegram.ext import Updater
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext,  CallbackQueryHandler
from telegram.ext import CommandHandler, MessageHandler, Filters
import os
import django
import re
import math


os.environ.setdefault('DJANGO_SETTINGS_MODULE', "juliaMoviesBot.settings")
django.setup()

from juliaMoviesBot.juliakinopoisk import JuliaMovie, JuliaUser
from telegrambot.models import TelegramUser, Movie, UserMovies
  


def start(update: Update, context: CallbackContext):
    current_chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=current_chat_id, text="Привет, я бот-синефил!")
    new_user(update.message.from_user.id)
    update.message.reply_markdown_v2(
        fr'Как вас зовут\?')

def new_user(user_tg_id):
    try:
        user = TelegramUser(telegram_id=user_tg_id)
        user.save()
        return True
    except:
        return False  

def input(update: Update, context: CallbackContext):
    user_tg_id = update.message.from_user.id
    text = update.message.text

    if 1:
        user = TelegramUser.objects.get(telegram_id=user_tg_id)
        user_status = user.status
        # statuses
        #
        # 0, user reg-ed, wait name
        # 1, name set-ed, or user input not needed
        # user input waits
        # 2, search by name,
        # 3, search by director,
        # 4, random by genre,
        
        if user_status == 0:
            user.name = str(text)
            user.status = 1
            user.save() 

            update.message.reply_text("Добро пожаловать,  {} 😊".format(text),
                reply_markup=main_menu_keyboard())

        elif user_status == 2:
            user.status = 1
            user.save()
            movie_name = update.message.text

            movie = JuliaMovie.searchByName(movie_name)
            if not movie:
                movie = "Фильм не найден. Неполадки какие-то"
                update.message.reply_text(text=movie,
                reply_markup=search_menu_keyboard())
            else:
                update.message.reply_text(text=movie,
                reply_markup=favorite_it_keyboard())
                update.message.reply_text(text=search_menu_message(user.name),
                reply_markup=search_menu_keyboard()) 
       

        elif user_status == 3:
            director_name = update.message.text 

            movies = JuliaMovie.searchByDirector(director_name)
            if not movies:
                movies = "Режиссер не найден. Неполадки какие-то"
            user.status = 1
            user.save()

            sts = next_st(math.ceil(len(movies)/4096))
            messages = slicer(movies,sts)

            for msg in messages:
                update.message.reply_text(text=msg)   


        elif user_status == 4:
            genre = update.message.text
            res = JuliaMovie.randomByGenre(genre)
            movie = "Не найдено. Неполадки"
            usr_st4_keyboard = favorite_it_keyboard()

            if not res['movie']:
                movie = "Не найдено. Попробуйте один из жанров\n" + res['genres']
                usr_st4_keyboard = None

            else:
                movie = res['movie']

            user.status = 1
            user.save()   

            update.message.reply_text(text=movie,
                reply_markup=usr_st4_keyboard) 
            update.message.reply_text(text=main_menu_message(),
                            reply_markup=main_menu_keyboard())            

    else:
        pass

def slicer(str,st):
    res = []
    prev = 0

    for i in st:
        res.append(str[prev:i])
        prev = i

    return res    

def next_st(st):
    res = []
    for i in range(1,st+1):
        num = 4096*i
        res.append(num)

    return res

def movie_name(update: Update, context: CallbackContext):
    update.message.reply_text(text=main_menu_message(),
                reply_markup=main_menu_keyboard())


def main_menu_keyboard():
    keyboard = [
        [
            KeyboardButton("/search"),
            KeyboardButton("/recommend"),
            KeyboardButton("/my_favorites"),
        ]
    ]
    
    return ReplyKeyboardMarkup(keyboard,resize_keyboard=True)


def search_menu_keyboard():
    keyboard = [
        [
            KeyboardButton("/by_name"),
            KeyboardButton("/by_director"),
            KeyboardButton("/main_menu"),
        ]
    ]    

    return ReplyKeyboardMarkup(keyboard,resize_keyboard=True)    

def favorite_it_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Избрать ❤️",callback_data="favorite_it"),         
        ]
    ]

    return InlineKeyboardMarkup(keyboard)   


def unfavorite_it_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Убрать 🚫",callback_data="unfavorite_it"),         
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def main_menu_message():
    return "Меню"

def search_menu_message(name):
    return "Как будем искать, {}?".format(name)    

def get_movie_name_message():
    return "Напишите название фильма"

def get_movie_director_message():
    return "Напишите фамилию режиссера"

def favorite_it_message():
    return "Избран 💜🖤💙💚💛"

def unfavorite_it_message():
    return "Удален 🚫🚫🚫🚫🚫"    

def get_recommend_message(name):
    return "Какой жанр предпочитаете, {}?".format(name)



def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    query.edit_message_text(text="Selected: {}".format(query.data))


def main_menu(update: Update, context: CallbackContext):
    update.message.reply_text(text=main_menu_message(),reply_markup=main_menu_keyboard())


def search(update: Update, context: CallbackContext):
    user_tg_id = update.message.from_user.id 
    user = TelegramUser.objects.get(telegram_id=user_tg_id)

    update.message.reply_text(text=search_menu_message(user.name),reply_markup=search_menu_keyboard())


def by_name(update: Update, context: CallbackContext):
    user_tg_id = update.message.from_user.id
    user = TelegramUser.objects.get(telegram_id=user_tg_id)
    user.status = 2
    user.save()

    update.message.reply_text(text=get_movie_name_message())

def by_director(update: Update, context: CallbackContext):
    user_tg_id = update.message.from_user.id 
    user = TelegramUser.objects.get(telegram_id=user_tg_id)
    user.status = 3
    user.save()

    update.message.reply_text(text=get_movie_director_message())

def favorite_it_btn(update: Update, context: CallbackContext):
    user_tg_id = update.callback_query.from_user.id 
    user = TelegramUser.objects.get(telegram_id=user_tg_id)

    movie = update.callback_query.message.text

    kinopoisk_movie_id = re.findall("(https:\//www.kinopoisk.ru\/film\/\d{1,20}/)",movie)
    kinopoisk_movie_id = re.findall("(\d{1,20})\/",kinopoisk_movie_id[0])

    movie = Movie(kinopoisk_id=kinopoisk_movie_id[0])
    try:
        movie.save()
    except:
        movie = Movie.objects.get(kinopoisk_id=kinopoisk_movie_id[0])

    favorite_movie = UserMovies(user=user,movie=movie)
    try:
        favorite_movie.save()
    except:
        pass 

    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text=favorite_it_message(),
    )

def unfavorite_it_btn(update: Update, context: CallbackContext):
    user_tg_id = update.callback_query.from_user.id 
    user = TelegramUser.objects.get(telegram_id=user_tg_id)

    movie = update.callback_query.message.text

    kinopoisk_movie_id = re.findall("(https:\//www.kinopoisk.ru\/film\/\d{1,20}/)",movie)
    kinopoisk_movie_id = re.findall("(\d{1,20})\/",kinopoisk_movie_id[0])

    movie = Movie.objects.get(kinopoisk_id=kinopoisk_movie_id[0])

    try:
        favorite_movie = UserMovies(user=user,movie=movie)
        favorite_movie.delete()
    except:
        pass 

    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text=unfavorite_it_message(),
    )


def my_favorites(update: Update, context: CallbackContext):
    user_tg_id = update.message.from_user.id 
    user = TelegramUser.objects.get(telegram_id=user_tg_id)

    user_favorites = UserMovies.objects.filter(user=user)

    movies = []

    for m in user_favorites:
        movies.append(JuliaMovie.getById(m.movie.kinopoisk_id))

    response_movies = ""

    for m in movies:
        if m != False:
            update.message.reply_text(text=m,reply_markup=unfavorite_it_keyboard())

    update.message.reply_text(text=main_menu_message(),
                            reply_markup=main_menu_keyboard())   


def recommend(update: Update, context: CallbackContext):
    user_tg_id = update.message.from_user.id 
    user = TelegramUser.objects.get(telegram_id=user_tg_id)

    user.status = 4
    user.save()

    update.message.reply_text(text=get_recommend_message(user.name))

# настройка
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
updater = Updater(token='', use_context=True)
dispatcher = updater.dispatcher
start_handler = CommandHandler('start', start)
input_handler = MessageHandler(Filters.text & ~Filters.command,input)
button_handler = CallbackQueryHandler(button)
search_handler = CommandHandler('search',search)
by_name_handler = CommandHandler('by_name',by_name)
by_director_handler = CommandHandler('by_director',by_director)
my_favorites_handler = CommandHandler('my_favorites',my_favorites)
recommend_handler = CommandHandler('recommend',recommend)
main_menu_handler = CommandHandler('main_menu',main_menu)
callback_handler = CallbackQueryHandler(favorite_it_btn,pattern='favorite_it')
callback_handler2 = CallbackQueryHandler(unfavorite_it_btn,pattern='unfavorite_it')


dispatcher.add_handler(start_handler)
dispatcher.add_handler(input_handler)
dispatcher.add_handler(main_menu_handler)
dispatcher.add_handler(search_handler)
dispatcher.add_handler(by_name_handler)
dispatcher.add_handler(by_director_handler)
dispatcher.add_handler(callback_handler)
dispatcher.add_handler(callback_handler2)
dispatcher.add_handler(my_favorites_handler)
dispatcher.add_handler(recommend_handler)


updater.start_polling()
updater.idle()
