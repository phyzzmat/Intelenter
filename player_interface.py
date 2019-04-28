from telegram.ext import MessageHandler, Filters, CommandHandler, ConversationHandler
from data_objects import *
from database import *
from random import choice
from information import *


participants = 3
Lounge = Lounge()


def check_if_finished(bot, update, room_interface, delete=True):

    for topic in room_interface.questions:
        for question in room_interface.questions[topic]:
            if not room_interface.questions[topic][question].answered:
                return 0
    if delete:
        Lounge.rooms[room_interface.number].players = {}
    return 1


def dismiss_question(bot, job):
    room_id, topic, points = job.context[:3]
    if check_if_finished(bot, 0, Lounge[room_id], delete=False):
        inform_about_finish(bot, 0, Lounge[room_id])
        Lounge[room_id].players = {}
        return ConversationHandler.END
    if not Lounge[room_id].questions[topic][points].answered:
        for player in Lounge[room_id].players:
            bot.send_message(
                chat_id=player,
                text="В течение 30 секунд на вопрос никто не ответил. "
                     "Ну и пусть. Ну и ладно. Вопрос выбирает предыдущий игрок."
            )
        Lounge[room_id].questions[topic][points].answered = 1
        Lounge[room_id].mode = "choosing"



def help_(bot, update):
    update.message.reply_text(
        "Добро пожаловать в нашего бота!\n"
        "Напишите /play, чтобы начать играть"
    )


def participate(bot, update, chat_data):
    update.message.reply_text(
        "Итак. Вы решили поиграть. Очень здорово. "
        "Введите Ваше имя."
    )
    return "enter_player_name"


def enter_player_name(bot, update, chat_data):
    update.message.reply_text(
        "Хорошо. Вы будете записаны под таким именем в таблицу результатов. "
        "А теперь введите номер комнаты, в которой вы будете играть."
    )
    chat_data["nick_name"] = update.message.text
    return "enter_room"


def enter_room(bot, update, chat_data):

    room = session.query(Room).filter_by(number=update.message.text).first()
    if room:

        chat_data["room"] = room.number
        # Если нет такой комнаты в нашем онлайн-списке, добавляем
        if room.number not in Lounge.rooms:
            Lounge.append(RoomData(room.number))

        room_interface = Lounge[room.number]
        print(room_interface)
        if len(room_interface.players) == participants:
            update.message.reply_text(
                "К сожалению, комната уже заполнена."
            )
        elif len(room_interface.players) == participants - 1:
            update.message.reply_text(
                "Ура! Вы заняли последнее место в комнате!"
            )
            Lounge[room.number].running = True
            Lounge[room.number][update.message.chat_id] = Player(
                name=chat_data["nick_name"],
                chat_id=update.message.chat_id,
            )
            inform_about_start(bot, update, room_interface)
            set_up(bot, update, chat_data)
        else:
            Lounge[room.number][update.message.chat_id] = Player(
                name=chat_data["nick_name"],
                chat_id=update.message.chat_id,
            )
            update.message.reply_text(
                "Вы успешно вошли в комнату. Сейчас в комнате "
                f"{len(room_interface.players)} участников. Игра начнется, "
                f"когда в комнату войдет {participants} участников."
            )

        return "playing"

    update.message.reply_text(
        "К сожалению, такой не существует. Попробуйте снова."
    )
    return "enter_room"


def set_up(bot, update, chat_data):
    room_id = chat_data["room"]
    Lounge[room_id].mode = "choosing"
    Lounge[room_id].choosing = choice(list(Lounge[room_id].players.keys()))
    for player in Lounge[room_id].players:
        bot.send_message(
            chat_id=player,
            text=f"Первый вопрос выбирает игрок "
                 f"{Lounge[room_id].players[Lounge[room_id].choosing].name}."
    )
    print_question_list(bot, update, Lounge[room_id])


def playing(bot, update, chat_data, job_queue):

    room_id = chat_data["room"]
    mode = Lounge[room_id].mode
    print(Lounge[room_id].cur_q)

    if mode == "choosing":
        choose_question(bot, update, chat_data, job_queue)
    elif mode == "answering":
        check_answer(bot, update, chat_data, room_id)


def check_answer(bot, update, chat_data, room_id):

    text = update.message.text
    chat_id = update.message.chat_id
    current_room = Lounge[room_id]
    topic, points = current_room.cur_q
    question = current_room.questions[topic][points]

    if (topic, points) not in current_room[chat_id].answered_q:
        current_room[chat_id].answered_q.add((topic, points))
        update.message.reply_text(
            "Хорошо, сейчас проверим..."
        )
        if text == question.answer:
            current_room[chat_id].points += question.points
            update.message.reply_text(
                f"Полное решение. +{question.points} б. "
                f"У вас {current_room[chat_id].points} б."
            )
            Lounge[room_id].choosing = chat_id
            Lounge[room_id].questions[topic][points].answered = 1
            Lounge[room_id].mode = "choosing"

            if check_if_finished(bot, update, Lounge[room_id]):
                inform_about_finish(bot, update, Lounge[room_id])
                return ConversationHandler.END
        else:
            current_room[chat_id].points -= question.points
            update.message.reply_text(
                f"Неправильный ответ на тесте 1. -{question.points} б. "
                f"У вас {current_room[chat_id].points} б."
            )
            if all([(topic, points) in Lounge[room_id][i].answered_q
                    for i in Lounge[room_id].players]):

                Lounge[room_id].questions[topic][points].answered = 1
                Lounge[room_id].mode = "choosing"
                if check_if_finished(bot, update, Lounge[room_id]):
                    inform_about_finish(bot, update, Lounge[room_id])
                    return ConversationHandler.END

        if Lounge[room_id].questions[topic][points].answered:
            inform_about_answer(bot, update, text, current_room, corr=text == question.answer)
            print_question_list(bot, update, current_room)
        else:
            inform_to_try_again(bot, update, text, current_room)
    else:
        update.message.reply_text(
            "Вы уже успели некорректно ответить."
        )
    return "playing"


def choose_question(bot, update, chat_data, job_queue):
    room_id = chat_data["room"]
    current_room = Lounge[room_id]
    t = update.message.text
    t = t.split(',')
    chat_id = update.message.chat_id
    try:
        topic, points = t
        points = int(points.strip())
        assert current_room.questions[topic][points].answered == 0
    except Exception as e:
        print(e)
        return "playing"
    else:
        if current_room.choosing != chat_id:
            update.message.reply_text(
                "Сейчас выбираете не Вы."
            )
        else:
            print_question(bot, update, Lounge[room_id], topic, points)
            Lounge[room_id].cur_q = (topic, points)
            Lounge[room_id].mode = "answering"
            job_queue.run_once(dismiss_question, TIME, context=[room_id, topic, points])
    return "playing"


def stop2(bot, update):
    update.message.reply_text(
        "Ех :("
    )
    for i in Lounge:
        del Lounge[i].players[update.message.chat_id]
    return ConversationHandler.END


def add_player_commands(dp):

    help_me = CommandHandler('help', help_)
    player_interface = ConversationHandler(

        entry_points=[CommandHandler('play', participate, pass_chat_data=1)],
        states={
            "enter_player_name":
                [MessageHandler(Filters.text,
                                enter_player_name,
                                pass_chat_data=1)],
            "playing":
                [MessageHandler(Filters.text,
                                playing,
                                pass_chat_data=1,
                                pass_job_queue=1)],
            "enter_room":
                [MessageHandler(Filters.text,
                                enter_room,
                                pass_chat_data=1)],
        },
        fallbacks=[CommandHandler('stop2', stop2)]
    )

    dp.add_handler(player_interface)
    dp.add_handler(help_me)