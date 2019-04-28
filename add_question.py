from telegram.ext import MessageHandler, Filters, CommandHandler, ConversationHandler
from database import *


def begin(bot, update, chat_data):

    update.message.reply_text(
        "Превосходно! Теперь напишите номер комнаты."
    )
    return "room_choice"


def choose_room(bot, update, chat_data):

    chat_data["room_to_add"] = update.message.text
    room = session.query(Room).first()

    if room:
        chat_data["password_to_add"] = room.password
        update.message.reply_text(
            "Комната с таким именем уже существует. Хотите зайти в нее? "
            "Введите пароль!"
        )
        return "password_to_existing_room"

    else:
        update.message.reply_text(
            "Такой комнаты еще нет. Придумайте пароль для нее."
        )
        return "create_new_room"


def password_to_existing_room(bot, update, chat_data):

    if update.message.text != chat_data["password_to_add"]:
        update.message.reply_text(
            "К сожалению, введённый пароль неверен."
            "Панель администратора закрыта."
        )
        return ConversationHandler.END

    update.message.reply_text(
        "Пароль верный. Теперь напишите через запятую тему вопроса и стоимость."
    )
    return "enter_topic_and_points"


def enter_statement(bot, update, chat_data):

    update.message.reply_text(
        "Хорошо. Осталось только ввести ответ."
    )
    chat_data["statement_to_add"] = update.message.text
    return "enter_answer"


def enter_answer(bot, update, chat_data):

    update.message.reply_text(
        "Спасибо! Вопрос добавлен. Добавим следующий? Для выхода напишите /stop. "
        "Или напишите через запятую тему вопроса и стоимость."
    )
    chat_data["answer_to_add"] = update.message.text

    new_question = Question(room=chat_data["room_to_add"],
                            statement=chat_data["statement_to_add"],
                            answer=chat_data["answer_to_add"],
                            points=chat_data["points_to_add"],
                            topic=chat_data["topic_to_add"])
    session.add(new_question)
    session.commit()

    return "enter_topic_and_points"


def enter_topic_and_points(bot, update, chat_data):

    data = update.message.text.split(',')

    try:
        topic, points = ','.join(data[:-1]), int(data[-1])
    except Exception:
        update.message.reply_text(
            "Произошла ошибка. Мы уже работаем над ее устранением."
        )
        return "enter_topic_and_points"
    else:
        chat_data["topic_to_add"] = topic
        chat_data["points_to_add"] = points
        update.message.reply_text(
            "Великолепно. Теперь введите условие вопроса."
        )
        return "enter_statement"


def create_new_room(bot, update, chat_data):

    new_room = Room(password=update.message.text,
                    number=chat_data["room_to_add"])
    session.add(new_room)
    session.commit()

    update.message.reply_text(
        "Комната успешно создана. Теперь напишите через запятую тему вопроса и стоимость."
    )
    return "enter_topic_and_points"


def stop(bot, update):

    update.message.reply_text(
        "Работа завершена."
    )
    return ConversationHandler.END


def add_admin_commands(dp):

    admin_mode = ConversationHandler(

        entry_points=[CommandHandler('admin', begin, pass_chat_data=1)],
        states={
            "room_choice":
                [MessageHandler(Filters.text,
                                choose_room,
                                pass_chat_data=1)],
            "password_to_existing_room":
                [MessageHandler(Filters.text,
                                password_to_existing_room,
                                pass_chat_data=1)],
            "create_new_room":
                [MessageHandler(Filters.text,
                                create_new_room,
                                pass_chat_data=1)],
            "enter_topic_and_points":
                [MessageHandler(Filters.text,
                                enter_topic_and_points,
                                pass_chat_data=1)],
            "enter_statement":
                [MessageHandler(Filters.text,
                                enter_statement,
                                pass_chat_data=1)],
            "enter_answer":
                [MessageHandler(Filters.text,
                                enter_answer,
                                pass_chat_data=1)],
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    dp.add_handler(admin_mode)
