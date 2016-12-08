from codex.baseerror import *
from codex.baseview import APIView
from wechat.models import *

import requests
import json
import time
import datetime


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


class NoticePanel(APIView):

    def get(self):
        # self.check_input('openid')
        user = User.objects.get(username='2014013434')
        response = requests.post('http://se.zhuangty.com:8000/curriculum/' + user.username)
        result = {
            'student_number': user.student_id,
            'notices': [],
            'assignments': [],
            'files': []
        }
        if response.status_code == 200:
            res = json.loads(response.content.decode())
            dic = {
                'read': '已读',
                'unread': '未读',
                True: '已批改',
                False: '未批改'
            }
            course_set = []
            for course in res['classes']:
                if course['courseid'] in course_set:
                    continue
                course_set.append(course['courseid'])
                response_inform = requests.post('http://se.zhuangty.com:8000/learnhelper/'
                                                + user.username + '/courses/' + course['courseid']
                                                + '/notices')
                if response_inform.status_code == 200:
                    resp = json.loads(response_inform.content.decode())
                    for notice in resp['notices']:
                        inform = {}
                        inform['title'] = notice['title']
                        inform['publish_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(notice['publishtime'] / 1000))
                        inform['state'] = dic[notice['state']]
                        inform['content'] = notice['content']
                        result['notices'].append(inform)
            course_set = []
            for course in res['classes']:
                if course['courseid'] in course_set:
                    continue
                course_set.append(course['courseid'])

                response_work = requests.post('http://se.zhuangty.com:8000/learnhelper/'
                                              + user.username + '/courses/' + course['courseid']
                                              + '/assignments')
                if response_work.status_code == 200:
                    resp = json.loads(response_work.content.decode())
                    for assignment in resp['assignments']:
                        work = {}
                        if assignment['duedate'] / 1000 > time.mktime(datetime.datetime.now().timetuple()):
                            work['processing'] = True
                        else:
                            work['processing'] = False
                        work['title'] = assignment['title']
                        work['detail'] = assignment['detail']
                        work['start_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(assignment['startdate'] / 1000))
                        work['end_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(assignment['duedate'] / 1000))
                        work['scored'] = dic[assignment['scored']]
                        work['evaluating_teacher'] = assignment['evaluatingteacher']
                        work['evaluating_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(assignment['evaluatingdate'] / 1000))
                        work['comment'] = assignment['comment']
                        work['grade'] = str(assignment['grade'])
                        result['assignments'].append(work)
            course_set = []
            for course in res['classes']:
                if course['courseid'] in course_set:
                    continue
                course_set.append(course['courseid'])
                response_work = requests.post('http://se.zhuangty.com:8000/learnhelper/'
                                              + user.username + '/courses/' + course['courseid']
                                              + '/documents')
                if response_work.status_code == 200:
                    resp = json.loads(response_work.content.decode())
                    for document in resp['documents']:
                        file = {}
                        file['title'] = document['title']
                        file['explanation'] = document['explanation']
                        file['updating_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(document['updatingtime'] / 1000))
                        file['state'] = document['state']
                        file['size'] = document['size']
                        file['download_url'] = document['url']
                        result['files'].append(file)
        return result
