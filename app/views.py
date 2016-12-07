from codex.baseerror import *
from codex.baseview import APIView
from wechat.models import User, Comment
import requests
import json
import time
import datetime
from XuetangPlus.settings import WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET
from wechat.wrapper import WeChatLib
from XuetangPlus.settings import CONFIGS

class UserBind(APIView):

    def validate_user(self):
        """
        input: self.input['student_id'] and self.input['password']
        raise: ValidateError when validating failed
        """
        dic = {'username': str(self.input['username']),
               'password': str(self.input['password'])}
        response = requests.post('http://se.zhuangty.com:8000/users/register', json = dic)
        if response.status_code == 200:
            res = json.loads(response.content.decode())
            user = User.get_by_openid(self.input['openid'])
            user.username = res['username']
            user.student_id = res['information']['studentnumber']
            user.department = res['information']['department']
            user.position = res['information']['position']
            user.email = res['information']['email']
            user.realname = res['information']['realname']
            user.save()
            return True
        raise NotImplementedError('username/student_id or password error')

    def get(self):
        self.check_input('openid')
        return User.get_by_openid(self.input['openid']).student_id

    def post(self):
        self.check_input('openid', 'username', 'password')
        self.validate_user()


class MyCourse(APIView):
    def get(self):
        self.check_input('openid')
        user = User.get_by_openid(self.input['openid'])
        if user.student_id == '':
            return {'valid': False}
        else:
            response = requests.post('http://se.zhuangty.com:8000/curriculum/' + user.username)
            if response.status_code == 200:
                res = json.loads(response.content.decode())
                dic = {
                    1: '8:00',
                    2: '9:50',
                    3: '13:30',
                    4: '15:20',
                    5: '17:05',
                    6: '19:20',
                }
                courses = []
                for course in res['classes']:
                    new_course = {}
                    new_course['课程代号'] = course['courseid']
                    new_course['课程名称'] = course['coursename']
                    new_course['课程星期'] = course['time'][0]
                    new_course['课程时间'] = dic[course['time'][1]]
                    new_course['课程教师'] = course['teacher']
                    new_course['课程教室'] = course['classroom']
                    new_course['课程周数'] = course['week']
                    courses.append(new_course)
                return {'valid': True,
                        'student_id': user.student_id,
                        'courses': courses}


class CourseInfo(APIView):
    def get(self):
        self.check_input('openid', 'course_id')
        user = User.get_by_openid(self.input['openid'])
        response = requests.post('http://se.zhuangty.com:8000/curriculum/' + user.username)
        result = {}
        if response.status_code == 200:
            res = json.loads(response.content.decode())
            dic = {
                1: '8:00',
                2: '9:50',
                3: '13:30',
                4: '15:20',
                5: '17:05',
                6: '19:20',
            }
            for course in res['classes']:
                if course['courseid'] == self.input['course_id']:
                    result['course_id'] = course['courseid']
                    result['course_day'] = course['time'][0]
                    result['course_time'] = dic[course['time'][1]]
                    result['course_teacher'] = course['teacher']
                    result['course_classroom'] = course['classroom']
                    result['course_week'] = self.map_week(course['week'])
                    result['course_name'] = course['coursename']

        response = requests.post('http://se.zhuangty.com:8000/learnhelper/' + user.username + '/courses')
        if response.status_code == 200:
            res = json.loads(response.content.decode())
            for course in res['courses']:
                if course['courseid'] == self.input['course_id']:
                    result['course_new_file'] = course['newfile']
                    result['course_unread_notice'] = course['unreadnotice']
                    result['course_unsubmitted_operations'] = course['unsubmittedoperations']
        return result

    def map_week(self, week_list):
        start = 0
        current = 0
        result = ''
        while current < 16:
            if week_list[current] == 0 and current > start:
                if current > start + 1:
                    result += str(start + 1) + '-' + str(current) + ','
                else:
                    result += str(current) + ','
                start = current + 1
            current += 1
        if current > start + 1:
            result += str(start + 1) + '-' + str(current)
        else:
            result += str(current)

        return result

class NoticePanel(APIView):
    def get(self):
        self.check_input('openid')
        user = User.get_by_openid(self.input['openid'])
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

class CourseComment(APIView):
    def get(self):
        params = self.input
        course_id = params['id']
        comments = Comment.objects.filter(courseid=course_id)

        answer = []
        for index in range(0, len(comments)):
            answer.append((str(index), comments[index].toJson()))

        return json.dumps({'comments': answer})

    def post(self):
        params = self.input
        mark = params['mark']
        comment = params['comment']
        isanonymouse = params['isanonymouse']
        userid = -1

        timestamp = time.mktime(datetime.datetime.now().timetuple())
        course_id = params['id']

        if isanonymouse == False:
            userid = self.user.id
        Comment.objects.create(courseid=course_id, commenttime=timestamp, commenter=userid, content=comment, score=int(mark))

        return 1

class Map(APIView):
    lib = WeChatLib(WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET)

    def get(self):
        if 'type' in self.input:
            params = self.input
            ans = self.lib.changeLocationIndex(params['lati'], params['longi'], params['type'])
            return ans
        elif 'keyword' in self.input:
            params = self.input
            ans = self.lib.getRecommendAddress(params['keyword'])
            return ans
        access_token = self.lib.get_wechat_access_token()
        ticket = self.lib.get_wechat_jsapi_ticket()
        answer = [('access_token', access_token), ('ticket', ticket)]
        result = json.dumps(dict(answer))
        print("get all tickets")

        return result

    def post(self):
        return

class AppInfo(APIView):

    def get(self):
        return {'app_id':CONFIGS['WECHAT_APPID'], 'app_secret': CONFIGS['WECHAT_SECRET']}