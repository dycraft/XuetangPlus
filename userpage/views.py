from codex.baseerror import *
from codex.baseview import APIView
from wechat.models import *
from XuetangPlus.settings import WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET
from wechat.wrapper import WeChatLib
from XuetangPlus.settings import CONFIGS
from util.time import *
from util.randomStr import *
import hashlib


import requests
import json
import time
import datetime

start_time = [
    '08:00',
    '09:50',
    '13:30',
    '15:20',
    '17:05',
    '19:20',
]


class AccountBind(APIView):

    def get(self):
        self.check_input('openid')

        try:
            user = User.get_by_openid(self.input['openid'])
            return {
                'student_id': user.student_id
            }

        except:
            LogicError('no such openid')

    def post(self):
        self.check_input('open_id', 'student_id', 'password')

        student_id = self.input['student_id']
        password = self.input['password']
        open_id = self.input['open_id']

        if not student_id and password:
            raise InputError('Empty student_id or password.')

        url = 'http://se.zhuangty.com:8000/users/register'
        params = {
            'username': student_id,
            'password': password
        }

        response = requests.post(url, json=params)
        result = json.loads(response.content.decode())

        if response.status_code == 200:

            try:

                user = User.get_by_openid(open_id)
                user.username = result['username']
                user.student_id = result['information']['studentnumber']
                user.department = result['information']['department']
                user.position = result['information']['position']
                user.email = result['information']['email']
                user.realname = result['information']['realname']
                user.save()

            except:
                raise LogicError('Duplicated username.')
        else:

            raise ValidateError('Wrong username or password.')


class CheckBind(APIView):

    def get(self):
        self.check_input('open_id')

        user = User.get_by_openid(self.input['open_id'])

        if user.student_id == '':
            return {
                'bind': False,
            }

        else:
            return {
                'bind': True,
                'student_id': user.student_id,
            }


class UnBind(APIView):

    def post(self):
        self.check_input('open_id')
        try:
            user = User.get_by_openid(self.input['open_id'])
            if user.student_id == '':
                raise LogicError('has not bind')

            else:
                user.username = ''
                user.student_id = ''
                user.department = ''
                user.position = ''
                user.email = ''
                user.realname = ''
                user.save()

        except:
            raise LogicError('does not exist openid')


class CourseList(APIView):

    def get(self):
        self.check_input('openid')
        user = User.get_by_openid(self.input['openid'])

        if user.student_id == '':
            raise LogicError('has not bind')

        url = 'http://se.zhuangty.com:8000/users/register' + user.student_id
        response = requests.post(url)

        if response.status_code == 200:
            result = json.loads(response.content.decode())

            classes = [[], [], [], [], [], [], []]
            for course in result['classes']:
                day = course['time'][0] - 1
                course['start'] = start_time[course['time'][1] - 1]
                classes[day].append(course)

            for i in range(7):
                classes[i] = sorted(classes[i], key=lambda d: d['start'])

            return {
                'classes': classes
            }

        else:
            raise LogicError('Response Error')


class NoticePanel(APIView):

    def get(self):
        self.check_input('openid')
        user = User.get_by_openid(self.input['openid'])

        if user.student_id == '':
            raise LogicError('user has not bind')

        url = 'http://se.zhuangty.com:8000/curriculum/' + user.student_id
        response = requests.post(url)

        return_val = {
            'student_number': user.student_id,
        }

        if response.status_code == 200:
            result = json.loads(response.content.decode())
            course_ids = list(set([c['courseid'] for c in result['classes']]))

            for course_id in course_ids:
                response_notice = requests.post('http://se.zhuangty.com:8000/learnhelper/'
                                                + user.student_id + '/courses/' + course_id
                                                + '/notices')

                if response_notice.status_code == 200:

                    result_notice = json.loads(response_notice.content.decode())

                    for notice in result_notice['notices']:
                        notice['publish_time'] = stamp2localstr(notice['publishtime'])

                    return_val['notices'] = result_notice['notices']

                else:
                    raise LogicError('Response Error')

                response_assignment = requests.post('http://se.zhuangty.com:8000/learnhelper/'
                                              + user.student_id + '/courses/' + course_id
                                              + '/assignments')

                if response_assignment.status_code == 200:
                    result_assignment = json.loads(response_assignment.content.decode())

                    for assignment in result_assignment['assignments']:

                        if assignment['duedate'] > current_stamp():
                            assignment['processing'] = True
                        else:
                            assignment['processing'] = False

                        assignment['start_time'] = stamp2localstr(assignment['startdate'])
                        assignment['end_time'] = stamp2localstr(assignment['duedate'])
                        assignment['evaluating_time'] = stamp2localstr(assignment['evaluatingdate'])

                    result_notice['assignments'] = result_assignment['assignments']

                else:
                    raise LogicError('Response Error')

                response_file = requests.post('http://se.zhuangty.com:8000/learnhelper/'
                                              + user.student_id + '/courses/' + course_id
                                              + '/documents')
                if response_file.status_code == 200:
                    result_file = json.loads( response_file.content.decode())

                    for file in result_file['documents']:
                        file['updating_time'] = stamp2localstr(file['updatingtime'])

                    return_val['files'] = result_file['documents']

                else:
                    raise LogicError('Response Error')

        return return_val


class CourseInfo(APIView):

    def get(self):
        self.check_input('openid', 'course_id')
        user = User.get_by_openid(self.input['openid'])

        url = 'http://se.zhuangty.com:8000/curriculum/'
        params = {
            user.student_id
        }

        response = requests.post('http://se.zhuangty.com:8000/curriculum/' + user.student_id)
        result = {}
        if response.status_code == 200:
            result_course = json.loads(response.content.decode())

            for course in result_course['classes']:
                if course['courseid'] == self.input['course_id']:
                    result = course
                    result['course_day'] = course['time'][0]
                    result['course_time'] = start_time[course['time'][1] - 1]
                    result['course_week'] = self.map_week(course['week'])

                    response = requests.post('http://se.zhuangty.com:8000/learnhelper/' + user.student_id + '/courses')
                    if response.status_code == 200:
                        res = json.loads(response.content.decode())
                        for course in res['courses']:
                            if course['courseid'] == self.input['course_id']:
                                result['course_new_file'] = course['newfile']
                                result['course_unread_notice'] = course['unreadnotice']
                                result['course_unsubmitted_operations'] = course['unsubmittedoperations']
                                return result

                        raise LogicError('No course new file')

                    raise LogicError('Response Error')

            raise LogicError('No course')

        else:
            raise LogicError('Response Error')


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

class ChatMenu(APIView):

    def get(self):
        self.check_input('openid')
        chats = Chatting.filter_by_openid(self.input['openid'])
        result = []
        for c in chats:
            dic = {}
            if(c.open_id1 == self.input['openid']):
                dic['communicator'] = c.open_id2
            else:
                dic['communicator'] = c.open_id1
            dic['head_content'] = ''
            x = Message.objects.filter(id = c.content)
            if len(x) > 0:
                dic['head_content'] = x[0].content
            dic['update_time'] = c.update_time
            dic['is_updated'] =c.is_updated
            result.append(dic)
        return sorted(result, key=lambda d: d['update_time'])

    def post(self):
        return


class ChatArea(APIView):

    def get(self):
        self.check_input('openid', 'communicator_id')
        chats = Chatting.filter_by_chater_id(self.input['openid'], self.input['communicator_id'])
        if len(chats) == 0:
            Chatting.objects.create(open_id1 = self.input['openid'], open_id2 = self.input['communicator_id'])
            return []

        msgs = Message.filter_by_chater_id(self.input['openid'], self.input['communicator_id'])
        for msg in msgs:
            if msg.create_time < int(current_stamp()) - 30 * 86400:
                msg.delete()

        return

    def post(self):
        return


class GetOpenId(APIView):

    def get(self):
        self.check_input('code')

        url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid='
        url += CONFIGS['WECHAT_APPID']
        url += '&secret='
        url += CONFIGS['WECHAT_SECRET']
        url += '&code='
        url += self.input['code']
        url += '&grant_type=authorization_code'

        response = requests.get(url)
        result = json.loads(response.content.decode())

        return {
            'openid': result['openid']
        }


class GetJSSDK(APIView):

    def get(self):
        self.check_input('url')

        confirm = WechatConfirmation.objects.get(id=1)
        jsapi_ticket = confirm.get_jssdk_ticket()

        current_url = self.input['url']
        new_url = ''
        for x in current_url:
            if x == '#':
                break
            new_url += x

        stamp = int(current_stamp())
        rstr = random_str()

        signature_string = 'jsapi_ticket='
        signature_string += jsapi_ticket
        signature_string += '&noncestr='
        signature_string += rstr
        signature_string += '&timestamp='
        signature_string += str(stamp)
        signature_string += '&url='
        signature_string += new_url

        signature = hashlib.sha1(signature_string.encode()).hexdigest()

        return {
            'app_id': CONFIGS['WECHAT_APPID'],
            'nonce_str': rstr,
            'timestamp': stamp,
            'signature': signature
        }


class EventDetail(APIView):
    def get(self):
        self.check_input('openid', 'id')
        user = User.get_by_openid(self.input['openid'])
        event_id_list = json.loads(user.event_list)
        event_list = sorted([Event.get_by_id(x) for x in event_id_list], key=lambda d: d.date)
        id = self.input['id']
        if len(event_list) > id:
            return {'name':event_list[id - 1].name, 'date': str(event_list[id - 1].date).split(' ')[0], 'content': event_list[id - 1].content}
        raise InputError('The given id is out of range')

    def post(self):

        self.check_input('openid', 'name', 'date', 'content')
        event = Event.objects.create(name = self.input['name'], date = datetime.datetime.strptime(self.input['date'], '%Y-%m-%d'), content = self.input['content'])
        id = User.get_by_openid(self.input['openid']).add_event(event.id)
        return {
                'id': id,
            }


class EventList(APIView):
    def get(self):
        self.check_input('openid')
        if 'date' not in self.input:
            date = datetime.date.today()
        else:
            date = datetime.datetime.strptime(self.input['date'], '%Y-%m-%d')
        user = User.get_by_openid(self.input['openid'])
        event_id_list = json.loads(user.event_list)
        event_list = sorted([Event.get_by_id(x) for x in event_id_list], key=lambda d: d.date)

        result = {}
        count = 0
        for e in event_list:
            if time.mktime(e.date.timetuple()) > time.mktime(date.timetuple()):
                count += 1
                e_date = str(e.date).split(' ')[0]
                if e_date in result:
                    result[e_date].append({'name':e.name, 'date': e_date, 'content': e.content})
                elif count < 10:
                    result[e_date] = [{'name':e.name, 'date': e_date, 'content': e.content}]
                else:
                    break
            else:
                user.del_event(e.id)
        return result

    def post(self):
        return