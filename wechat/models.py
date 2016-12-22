from django.db import models

from codex.baseerror import LogicError
import json
import time
from XuetangPlus.settings import CONFIGS
import requests
import datetime
from django.utils import timezone


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

class WechatConfirmation(models.Model):
    access_token = models.CharField(max_length=1024, default='')
    jssdk_ticket = models.CharField(max_length=1024, default='')
    access_token_expire_time = models.IntegerField(default=0)
    jssdk_ticket_expire_time = models.IntegerField(default=0)

    def get_access_token(self):
        print("get access")
        if time.mktime(datetime.datetime.now().timetuple()) >= self.access_token_expire_time:
            print("get a new access")
            access_token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='
            access_token_url += CONFIGS['WECHAT_APPID']
            access_token_url += '&secret='
            access_token_url += CONFIGS['WECHAT_SECRET']

            response = requests.get(access_token_url)
            result = json.loads(response.content.decode())

            self.access_token = result['access_token']
            self.access_token_expire_time = time.mktime(datetime.datetime.now().timetuple()) + result['expires_in'] - 300
            self.save()
            print('Got access token %s', self.access_token)
        print("mytoken")
        print(self.access_token)
        return self.access_token

    def get_jssdk_ticket(self):
        print("get jssdk")
        if time.mktime(datetime.datetime.now().timetuple()) >= self.jssdk_ticket_expire_time:
            print("get a new jssdk")
            jsapi_ticket_url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token='
            jsapi_ticket_url += self.get_access_token()
            jsapi_ticket_url += '&type=jsapi'

            response = requests.get(jsapi_ticket_url)
            result = json.loads(response.content.decode())

            self.jssdk_ticket = result['ticket']
            self.jssdk_ticket_expire_time = time.mktime(datetime.datetime.now().timetuple()) + result['expires_in'] - 300
            self.save()
            print(self.jssdk_ticket)
        return self.jssdk_ticket


class Chatting(models.Model):
    open_id1 = models.IntegerField(default=0)
    open_id2 = models.IntegerField(default=0)
    content = models.IntegerField(default=-1)
    update_time = models.DateTimeField(default=timezone.now)
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
    create_time = models.DateTimeField(default=timezone.now)


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