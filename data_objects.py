from database import *
from random import randint

class Lounge:
# Зал, в котором много комнат. Невозможно хранить все данные в chat_data, поскольку они не индивидуальны.
# Например, часто нужно разослать сообщение всем участникам комнаты.
    
    def __init__(self):
        self.rooms = {}

    def append(self, room):
        self.rooms[room.number] = room

    def __getitem__(self, item):
        return self.rooms[item]

    def __setitem__(self, item, value):
        self.rooms[item] = value

    def __delitem__(self, key):
        del self.rooms[key]


class RoomData:

    def __init__(self, number, participants):
        self.participants = participants # количество разрешенных участков
        self.players = {} # список игроков комнаты
        self.number = number # номер комнаты
        self.running = False
        self.mode = False # режим комнаты (выбор вопроса или ответ на вопрос)
        self.answering = None # deprecated
        self.choosing = None # ID игрока, который выбирает
        self.cur_q = None # Вопрос на данный момент
        self.hash_f = randint(1, 10**9)
        self.questions = {} # Словарь вопросов в комнате
        self.query()

    def query(self):
        q = session.query(Question).filter_by(room=self.number).all()
        for question in q:
            if question.topic not in self.questions:
                self.questions[question.topic] = {}
            self.questions[question.topic][question.points] = QuestionInstance(question)

    def __getitem__(self, item):
        return self.players[item]

    def __setitem__(self, item, value):
        self.players[item] = value


class QuestionInstance:

    def __init__(self, class_object):
        self.answered = 0 # использован ли (т.е. вообще поднимался ли вопрос)
        self.answer = class_object.answer # ответ
        self.statement = class_object.statement # условие
        self.points = class_object.points # количество баллов
        self.topic = class_object.topic # тема


class Player:

    def __init__(self, chat_id, name):
        self.points = 0
        self.chat_id = chat_id
        self.name = name
        self.answered_q = set()
