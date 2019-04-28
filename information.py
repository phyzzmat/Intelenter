TIME = 30

def inform_about_start(bot, update, room_interface):
    print(room_interface.players)
    for player in room_interface.players:
        bot.send_message(
            chat_id=player,
            text="Ура! Игра началась!"
        )

def inform_about_answer(bot, update, answer, room_interface, corr=0):
    for player in room_interface.players:
        bot.send_message(
            chat_id=player,
            text=f"Был дан {'' if corr else 'не'}верный ответ: "
                 f"{answer}. Следующий вопрос выбирает "
                 f"{room_interface[room_interface.choosing].name}."
        )


def inform_about_finish(bot, update, room_interface):
    results = ["Результаты."]
    for i in room_interface.players:
        results.append(f'{room_interface.players[i].name}: {room_interface.players[i].points} б.')
    for player in room_interface.players:
        bot.send_message(
            chat_id=player,
            text='\n'.join(results))


def print_question_list(bot, update, room_interface):
    for player in room_interface.players:
        bot.send_message(
            chat_id=player,
            text="Вопросы:\n"
        )
        s = []
        for topic in room_interface.questions:
            s.append(f"""Тема: {topic}. Вопросы: {', '.join(
                [str(i.points) for i in room_interface.questions[topic].values() if
                 not i.answered]
            )}""")
        bot.send_message(
            chat_id=player,
            text='\n'.join(s)
        )


def print_question(bot, update, room_interface, topic, points):
    global TIME
    question = room_interface.questions[topic][points]
    for player in room_interface.players:
        bot.send_message(
            chat_id=player,
            text=f"(На ответ {TIME} секунд) Вопрос. {question.statement}"
        )


def inform_to_try_again(bot, update, answer, room_interface):
    for player in room_interface.players:
        bot.send_message(
            chat_id=player,
            text=f"Был дан неверный ответ: {answer}. Попробуйте ответить, если еще не пробовали."
        )
