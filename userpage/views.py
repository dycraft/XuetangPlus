from codex.baseerror import *
from codex.baseview import APIView
from wechat.models import *

import requests
import json


class AccountBind(APIView):

    def get(self):
        self.check_input('openid')
        user = User.get_by_openid(self.input['openid'])
        return {
            'student_id': user.student_id,
            'username': user.username
        }

    def post(self):
        self.check_input('username', 'password')

        username = self.input['username']
        password = self.input['password']
        if not username and password:
            raise InputError('Empty username or password.')

        url = 'http://se.zhuangty.com:8000/users/register'
        params = {
            'username': username,
            'password': password
        }

        response = requests.post(url, json=params)
        result = json.loads(response.content.decode())
        if response.status_code == 200 and result['message'] == 'Success':
            if not len(User.objects.filter(username=username)):
                user = User.objects.create()
                user.username = result['username']
                user.student_id = result['information']['studentnumber']
                user.department = result['information']['department']
                user.position = result['information']['position']
                user.email = result['information']['email']
                user.realname = result['information']['realname']
                user.save()
            else:
                raise LogicError('Duplicated username.')
        else:
            raise ValidateError('Wrong username or password.')


class CourseList(APIView):

    def get(self):
        url = 'http://se.zhuangty.com:8000/curriculum/' + '2014013434'
        response = requests.post(url)
        result = json.loads(response.content.decode())
        if response.status_code == 200 and result['message'] == 'Success':
            start_time = [
                '08:00',
                '09:50',
                '13:30',
                '15:20',
                '17:05',
                '19:20',
            ]
            temp = result['classes']
            classes = [[], [], [], [], [], [], []]
            for t in temp:
                day = t['time'][0] - 1
                classes[day].append({
                    'start': start_time[t['time'][1] - 1],
                    'coursename': t['coursename'],
                    'classroom': t['classroom']
                })
            for i in range(7):
                classes[i] = sorted(classes[i], key=lambda d: d['start'])
            return {
                'classes': classes
            }
        else:
            raise ValidateError('Illegal username.')
