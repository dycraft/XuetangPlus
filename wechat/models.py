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
    notice_list = models.CharField(max_length=8192, default='[]')
    avatar_url = models.CharField(max_length=8192, default='')

    def add_notice(self, name):
        notices = json.loads(self.notice_list)
        notices.append(name)
        self.notice_list = json.dumps(notices)
        self.save()

    def get_read_notice_list(self):
        return json.loads(self.notice_list)

    def add_event(self, id):
        events = json.loads(self.event_list)
        events.append(id)
        self.event_list = json.dumps(events)
        self.save()
        return len(events)

    def search_event(self, id):
        events = json.loads(self.event_list)
        return events.index(id) + 1

    def del_event(self, id):
        if id > len(self.event_list):
            raise LogicError('The given id is out of range')
        events = json.loads(self.event_list)
        Event.get_by_id(events[id - 1]).delete()
        del(events[id - 1])
        self.event_list = json.dumps(events)

    def search_event(self, id):
        events = json.loads(self.event_list)
        return events.index(id)

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
    chatmsg = models.CharField(max_length=1024, default='[]')
    newchatmsg = models.CharField(max_length=1024, default='[]')
    ismsgupdated = models.IntegerField(default=0)

    def add_msg(self, open_id, content):
        msg = Message.objects.create(sender_id=open_id, course_id = self.courseid, content=content, create_time=0)
        self.newchatmsg = json.dumps(json.loads(self.newchatmsg).append(msg.id))
        self.ismsgupdated = 1
        self.save()

    def update_msg(self):
        self.ismsgupdated = 1
        self.save()

    def get_new_msg(self):
        answer = []
        i = 0
        for msgid in json.loads(self.newchatmsg):
            answer.append((i, Message.objects.get(id=msgid).to_json()))
            i = i + 1

        self.ismsgupdated = 0
        self.newchatmsg = '[]'
        self.save()

        return json.dumps(dict(answer))

    def get_old_msg(self):
        temp = json.loads(self.chatmsg)
        length = len(temp)
        return [Message.objects.get(id = x) for x in temp[length - 10, length]]

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


class Message(models.Model):
    sender_id = models.CharField(max_length=128, default='')
    course_id = models.CharField(max_length=128, default='')
    content = models.CharField(max_length=1024, default='')
    create_time = models.DateTimeField(default=timezone.now)

    def to_json(self):
        answer = []
        answer.append(('sender_id', self.sender_id))
        answer.append(('course_id', self.course_id))
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
