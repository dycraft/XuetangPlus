from django.db import models

from codex.baseerror import LogicError
import json
import datetime


class User(models.Model):
    open_id = models.CharField(max_length=64, unique=True, db_index=True)
    student_id = models.CharField(max_length=32, db_index=True)
    username = models.CharField(max_length=32, db_index=True, default='')
    department = models.CharField(max_length=64, default='')
    position = models.CharField(max_length=32, default='')
    email = models.CharField(max_length=32, default='')
    realname = models.CharField(max_length=32, default='')
    event_list = models.CharField(max_length=256, default='[]')

    def add_event(self, id):
        events = json.loads(self.event_list)
        events.append(id)
        self.event_list = json.dumps(events)
        self.save()
        return len(events)

    def del_event(self, id):
        events = json.loads(self.event_list)
        if id in events:
            events.remove(id)
            Event.get_by_id(id).delete()
        self.event_list = json.dumps(events)
        self.save()
        return len(events)

    @classmethod
    def get_by_openid(cls, openid):
        try:
            return cls.objects.get(open_id=openid)
        except cls.DoesNotExist:
            raise LogicError('User not found')


class Course(models.Model):
    name = models.CharField(max_length=128)
    courseid = models.CharField(max_length=128)
    comments = models.CharField(max_length=1024, default='[]')


class Comment(models.Model):
    courseid = models.IntegerField(default=0)
    commenttime = models.IntegerField(default=0)
    commenter = models.IntegerField(default=0)
    content = models.CharField(max_length=512, default='')
    score = models.IntegerField()

    def get_commenter_name(self):
        if self.commenter == -1:
            return 'anonymous'
        else:
            return User.objects.get(id=self.commenter)

    def to_json(self):
        answer = []
        answer.append(('courseid', self.courseid))
        answer.append(('commenttime', self.commenttime))
        answer.append(('commenter', self.commenter))
        answer.append(('content', self.content))
        answer.append(('score', self.score))
        return json.dumps(dict(answer))


class Chatting(models.Model):
    open_id1 = models.IntegerField(default=0)
    open_id2 = models.IntegerField(default=0)
    content = models.IntegerField(default=-1)
    update_time = models.DateTimeField(default=datetime.datetime.now())
    is_updated = models.IntegerField(default=0)

    @classmethod
    def filter_by_chater_id(cls, id1, id2):
        return cls.objects.filter(open_id1=id1, open_id2=id2) + cls.objects.filter(open_id1=id2, open_id2=id1)

    @classmethod
    def filter_by_openid(cls, openid):
        return cls.objects.filter(open_id1=openid) + cls.objects.filter(open_id2=openid)

    def to_json(self):
        answer = []
        answer.append(('open_id1', self.open_id1))
        answer.append(('open_id2', self.open_id2))
        answer.append(('content', self.content))
        answer.append(('isupdated', self.is_updated))
        return json.dumps(dict(answer))


class Message(models.Model):
    sender_id = models.CharField(max_length=128, default='')
    receiver_id = models.CharField(max_length=128, default='')
    content = models.CharField(max_length=1024, default='')
    create_time = models.DateTimeField(default=datetime.datetime.now())


    @classmethod
    def filter_by_chater_id(cls, id1, id2):
        return cls.objects.filter(sender_id=id1, receiver_id=id2) + cls.objects.filter(sender_id=id2, receiver_id=id1)

    def to_json(self):
        answer = []
        answer.append(('sender_id', self.sender_id))
        answer.append(('receiver_id', self.receiver_id))
        answer.append(('content', self.content))
        answer.append(('create_time', self.create_time))
        return json.dumps(dict(answer))


class Event(models.Model):
    name = models.CharField(max_length=128, default='')
    date = models.DateTimeField()
    content = models.CharField(max_length=512, default='')

    @classmethod
    def get_by_id(cls, id):
        try:
            return cls.objects.get(id=id)
        except cls.DoesNotExist:
            raise LogicError('User not found')