from django.db import models

from codex.baseerror import LogicError
import json
import time
from XuetangPlus.settings import CONFIGS
import requests
import datetime
from django.utils import timezone
from util.time import *


class User(models.Model):
    open_id = models.CharField(max_length=64, unique=True, db_index=True)
    student_id = models.CharField(max_length=32, db_index=True)
    username = models.CharField(max_length=32, db_index=True, default='')
    department = models.CharField(max_length=64, default='')
    position = models.CharField(max_length=32, default='')
    email = models.CharField(max_length=32, default='')
    realname = models.CharField(max_length=32, default='')
    event_list = models.CharField(max_length=1024, default='[]')
    notice_list = models.CharField(max_length=4096, default='[]')
    assignment_list = models.CharField(max_length=4096, default='[]')
    slide_list = models.CharField(max_length=8192, default='[]')
    avatar_url = models.CharField(max_length=4096, default='')

    def add_notice(self, name):
        notices = json.loads(self.notice_list)
        if name not in notices:
            notices.append(name)
            self.notice_list = json.dumps(notices)
            self.save()

    def add_assignment(self, name):
        assignments = json.loads(self.assignment_list)
        if name not in assignments:
            assignments.append(name)
            self.assignment_list = json.dumps(assignments)
            self.save()

    def add_slide(self, name):
        slides = json.loads(self.slide_list)
        if name not in slides:
            slides.append(name)
            self.slide_list = json.dumps(slides)
            self.save()

    def get_read_notice_list(self):
        return json.loads(self.notice_list)

    def get_read_assignment_list(self):
        return json.loads(self.assignment_list)

    def get_read_slide_list(self):
        return json.loads(self.slide_list)

    def add_event(self, id):
        events = json.loads(self.event_list)
        events.append(id)
        self.event_list = json.dumps(events)
        self.save()
        return len(events) - 1

    def search_event(self, id):
        events = json.loads(self.event_list)
        return events.index(id)

    def del_event(self, id):
        if id >= len(self.event_list):
            raise LogicError('The given id is out of range')
        events = json.loads(self.event_list)
        Event.get_by_id(events[id]).delete()
        del events[id]
        self.event_list = json.dumps(events)
        self.save()

    @classmethod
    def get_by_openid(cls, openid):
        try:
            return cls.objects.get(open_id=openid)
        except cls.DoesNotExist:
            raise LogicError('User not found')


class Course(models.Model):
    name = models.CharField(max_length=128, default='')
    course_id = models.CharField(max_length=128, default='')
    comments = models.CharField(max_length=1024, default='[]')
    chatmsg = models.CharField(max_length=1024, default='[]')

    def add_msg(self, open_id, content):
        msg = Message.objects.create(sender_id=open_id, course_id=self.course_id, content=content, create_time=current_stamp())
        temp = json.loads(self.chatmsg)
        temp.append(msg.id)
        self.chatmsg = json.dumps(temp)
        self.save()

    def get_msg(self):
        temp = json.loads(self.chatmsg)
        length = len(temp)
        if length < 10:
            return [Message.objects.get(id = x) for x in temp[::-1]]
        else:
            return [Message.objects.get(id = x) for x in temp[(length - 10):length][::-1]]


class CourseForSearch(models.Model):
    course_seq = models.CharField(max_length=128)
    course_name = models.CharField(max_length=128)
    score = models.CharField(max_length=128)
    feature = models.CharField(max_length=128)
    intro = models.CharField(max_length=128)
    time = models.CharField(max_length=128)
    second = models.CharField(max_length=128)
    school = models.CharField(max_length=128)
    teacher = models.CharField(max_length=128)
    course_id = models.CharField(max_length=128)
    week = models.CharField(max_length=128)
    year = models.CharField(max_length=128)

    @classmethod
    def fuzzy_search(cls, key_word):
        result_dict = []

        for x in CourseForSearch.objects.all():
            search_score = 0
            for c in key_word:
                if c == '':
                    continue
                for c1 in x.course_name:
                    if c1 == c:
                        search_score += 1000
                for c2 in x.school:
                    if c2 == c:
                        search_score += 2

                for c3 in x.feature:
                    if c3 == c:
                        search_score += 1

            if search_score != 0:
                result_dict.append({'course':x, 'search_score': search_score})

        if result_dict != []:
            result_dict = sorted(result_dict, key=lambda x:x['search_score'], reverse=True)

        return [x['course'] for x in result_dict]


class Comment(models.Model):
    course_id = models.CharField(max_length=128, default='')
    course_name = models.CharField(max_length=128, default='')
    comment_time = models.CharField(max_length=128, default='')
    commenter_id = models.IntegerField(default=0)
    content = models.CharField(max_length=512, default='')
    score = models.IntegerField(default=0)
    isanonymous = models.IntegerField(default=0)

    def get_commenter_name(self):
        if self.isanonymous == 0:
            return '匿名'
        else:
            return User.objects.get(id=self.commenter_id).realname


class WechatConfirmation(models.Model):
    access_token = models.CharField(max_length=1024, default='')
    jssdk_ticket = models.CharField(max_length=1024, default='')
    access_token_expire_time = models.IntegerField(default=0)
    jssdk_ticket_expire_time = models.IntegerField(default=0)

    def get_access_token(self):
        if time.mktime(datetime.datetime.now().timetuple()) >= self.access_token_expire_time:

            access_token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='
            access_token_url += CONFIGS['WECHAT_APPID']
            access_token_url += '&secret='
            access_token_url += CONFIGS['WECHAT_SECRET']

            response = requests.get(access_token_url)
            result = json.loads(response.content.decode())

            self.access_token = result['access_token']
            self.access_token_expire_time = time.mktime(datetime.datetime.now().timetuple()) + result['expires_in'] - 300
            self.save()

        return self.access_token

    def get_jssdk_ticket(self):

        if time.mktime(datetime.datetime.now().timetuple()) >= self.jssdk_ticket_expire_time:

            jsapi_ticket_url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token='
            jsapi_ticket_url += self.get_access_token()
            jsapi_ticket_url += '&type=jsapi'

            response = requests.get(jsapi_ticket_url)
            result = json.loads(response.content.decode())

            self.jssdk_ticket = result['ticket']
            self.jssdk_ticket_expire_time = time.mktime(datetime.datetime.now().timetuple()) + result['expires_in'] - 300
            self.save()

        return self.jssdk_ticket

    @classmethod
    def get_or_create(cls):
        elems = cls.objects.all()
        if len(elems) == 0:
            cls.objects.create()
        return cls.objects.all()[0]


class Message(models.Model):
    sender_id = models.CharField(max_length=128, default='')
    course_id = models.CharField(max_length=128, default='')
    content = models.CharField(max_length=1024, default='')
    create_time = models.CharField(max_length=128, default='')

    def to_json(self):
        answer = []
        answer.append(('sender_id', self.sender_id))
        answer.append(('course_id', self.course_id))
        answer.append(('content', self.content))
        answer.append(('create_time', self.create_time))
        return json.dumps(dict(answer))


class Event(models.Model):
    name = models.CharField(max_length=128, default='')
    date = models.CharField(max_length=128, default='')
    content = models.CharField(max_length=512, default='')

    @classmethod
    def get_by_id(cls, id):
        try:
            return cls.objects.get(id=id)
        except cls.DoesNotExist:
            raise LogicError('Event not found')
