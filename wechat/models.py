from django.db import models

from codex.baseerror import LogicError
import json
import time
from XuetangPlus.settings import CONFIGS
import requests
import datetime


class User(models.Model):
    open_id = models.CharField(max_length=64, unique=True, db_index=True)
    student_id = models.CharField(max_length=32, db_index=True)
    username = models.CharField(max_length=32, db_index=True, default='')
    department = models.CharField(max_length=64, default='')
    position = models.CharField(max_length=32, default='')
    email = models.CharField(max_length=32, default='')
    realname = models.CharField(max_length=32, default='')

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

    def toJson(self):
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