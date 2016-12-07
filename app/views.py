from codex.baseerror import *
from codex.baseview import APIView
from wechat.models import User
import requests
import json

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
                    result['week'] = course['week']

        response = requests.post('http://se.zhuangty.com:8000/learnhelper/' + user.username + '/courses')
        if response.status_code == 200:
            res = json.loads(response.content.decode())
            for course in res['courses']:
                if course['courseid'] == self.input['course_id']:
                    result['course_newfile'] = course['newfile']
                    result['course_unreadnotice'] = course['unreadnotice']
                    result['course_name'] = course['coursename']
                    result['course_unsubmittedoperations'] = course['unsubmittedoperations']
        return result

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