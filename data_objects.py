from database import *


class Lounge:

    def __init__(self):
        self.rooms = {}

    def append(self, room):
        self.rooms[room.number] = room

    def __getitem__(self, item):
        return self.rooms[item]

    def __setitem__(self, item, value):
        self.rooms[item] = value


class RoomData:

    def __init__(self, number):
        self.players = {}
        self.number = number
        self.running = False
        self.mode = False
        self.answering = None
        self.choosing = None
        self.cur_q = None
        self.questions = {}
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
        self.answered = 0
        self.answer = class_object.answer
        self.statement = class_object.statement
        self.points = class_object.points
        self.topic = class_object.topic


class Player:

    def __init__(self, chat_id, name):
        self.points = 0
        self.chat_id = chat_id
        self.name = name
        self.answered_q = set()
