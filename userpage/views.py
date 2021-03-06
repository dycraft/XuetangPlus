from codex.baseerror import *
from codex.baseview import APIView
from wechat.models import *
from wechat.views import event_urls
from XuetangPlus.settings import CONFIGS, get_redirect_url
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
        self.check_input('open_id')

        try:
            user = User.get_by_openid(self.input['open_id'])
            return {
                'student_id': user.student_id
            }

        except:
            raise LogicError('no such open_id')

    def post(self):
        self.check_input('open_id', 'student_id', 'password')

        student_id = self.input['student_id']
        password = self.input['password']
        open_id = self.input['open_id']

        if not (student_id and password):
            raise InputError('Empty student_id or password.')

        url = 'http://se.zhuangty.com:8000/users/register'
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
            'username': student_id,
            'password': password
        }

        response = requests.post(url, json=params)
        result = json.loads(response.content.decode())

        if response.status_code == 200:

            try:
                user = User.get_by_openid(open_id)
            except:
                raise LogicError('no such open_id')
            user.username = result['username']
            user.student_id = result['information']['studentnumber']
            user.department = result['information']['department']
            user.position = result['information']['position']
            user.email = result['information']['email']
            user.realname = result['information']['realname']
            user.save()
            url = 'http://se.zhuangty.com:8000/curriculum/' + user.student_id
            params = {
                'apikey': 'camustest',
                'apisecret': 'camustest',
            }
            response = requests.post(url, json=params)
            course_ids = []
            if response.status_code == 200:
                response_course = json.loads(response.content.decode())
                course_ids = []
                for c in response_course['classes']:
                    course_ids.append(c['courseid'])
                    cs = Course.objects.filter(course_id=c['courseid'])
                    if len(cs) == 0:
                        Course.objects.create(name=c['coursename'], course_id=c['courseid'])
                    elif cs[0].name != c['coursename']:
                        cs[0].name = c['coursename']
                        cs[0].save()


                course_ids = list(set(course_ids))
            else:
                raise LogicError("Response Error in AccountBind")

            for course_id in course_ids:
                response_notice = requests.post('http://se.zhuangty.com:8000/learnhelper/'
                                                + user.student_id + '/courses/' + course_id
                                                + '/notices')
                if response_notice.status_code == 200:
                    result_notice = json.loads(response_notice.content.decode())

                    for notice in result_notice['notices']:
                        user.add_notice(ReadNoticeRecord.notice_name(notice['title'], course_id))
                else:
                    raise LogicError("Response Error in AccountBind")
                response_assignment = requests.post('http://se.zhuangty.com:8000/learnhelper/'
                                                    + user.student_id + '/courses/' + course_id
                                                    + '/assignments')
                if response_assignment.status_code == 200:
                    result_assignment = json.loads(response_assignment.content.decode())

                    for assignment in result_assignment['assignments']:
                        user.add_assignment(ReadNoticeRecord.notice_name(assignment['title'], course_id))
                else:
                    raise LogicError("Response Error in AccountBind")

                response_slide = requests.post('http://se.zhuangty.com:8000/learnhelper/'
                                               + user.student_id + '/courses/' + course_id
                                               + '/documents')
                if response_slide.status_code == 200:
                    result_slide = json.loads(response_slide.content.decode())

                    for slide in result_slide['documents']:
                        user.add_slide(ReadNoticeRecord.notice_name(slide['title'], course_id))
                else:
                    raise LogicError("Response Error in AccountBind")
        else:
            raise ValidateError('Wrong username or password.')


class CheckBind(APIView):

    def get(self):
        self.check_input('open_id')
        try:
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

        except:
            raise LogicError('no such open_id')


class UnBind(APIView):

    def post(self):
        self.check_input('open_id')
        try:
            user = User.get_by_openid(self.input['open_id'])
        except:
            raise LogicError('no such open_id')
        if user.student_id == '':
            raise LogicError('user not bound')

        else:
            user.username = ''
            user.student_id = ''
            user.department = ''
            user.position = ''
            user.email = ''
            user.realname = ''
            user.save()


class CourseList(APIView):

    def get(self):
        self.check_input('open_id')
        try:
            user = User.get_by_openid(self.input['open_id'])
        except:
            raise LogicError('no such open_id')

        if user.student_id == '':
            raise LogicError('unbind user')

        url = 'http://se.zhuangty.com:8000/curriculum/' + user.student_id
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)

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
            raise LogicError('Response error')


class NoticeList(APIView):

    def get(self):
        self.check_input('open_id', 'page')

        try:
            pagenum = int(self.input['page'])
        except:
            raise InputError('The given page should be int')
        try:
            user = User.get_by_openid(self.input['open_id'])
        except:
            raise LogicError('no such open_id')
        read_notices = user.get_read_notice_list()
        if user.student_id == '':
            raise LogicError('user not bound')

        url = 'http://se.zhuangty.com:8000/curriculum/' + user.student_id
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        course_ids = []
        if response.status_code == 200:
            response_course = json.loads(response.content.decode())
            course_ids = list(set([c['courseid'] for c in response_course['classes']]))
        else:
            raise LogicError("Response Error in NoticeList")

        result = []

        for course_id in course_ids:
            response_notice = requests.post('http://se.zhuangty.com:8000/learnhelper/'
                                            + user.student_id + '/courses/' + course_id
                                            + '/notices')
            if response_notice.status_code == 200:
                result_notice = json.loads(response_notice.content.decode())

                for rc in response_course['classes']:
                    if rc['courseid'] == course_id:
                        course_name = rc['coursename']
                        break

                for notice in result_notice['notices']:
                    notice['coursename'] = course_name
                    notice['read'] = ReadNoticeRecord.notice_name(notice['title'], course_id) in read_notices

                result += result_notice['notices']
            else:
                raise LogicError("Response Error in NoticeList")

        length = len(result)
        result = sorted(result, key=lambda n: n['publishtime'], reverse=True)[10 * (pagenum - 1): 10 * pagenum]
        unread = 0
        for index, r in enumerate(result):
            r['index'] = index + 1
            r['title'] = r['title'].replace('&nbsp;', '')
            r['publishtime'] = stamp_to_localstr_date(r['publishtime'])
            r['content'] = r['content'].replace('\r\n', '</br>')
            if not r['read']:
                unread += 1

        return {
            'total': length,
            'notices': result,
            'unread': unread
        }


class AssignmentList(APIView):

    def get(self):
        self.check_input('open_id', 'page')

        try:
            pagenum = int(self.input['page'])
        except:
            raise InputError('The given page should be int')
        try:
            user = User.get_by_openid(self.input['open_id'])
        except:
            raise LogicError('no such open_id')
        read_assignments = user.get_read_assignment_list()
        if user.student_id == '':
            raise LogicError('user not bound')

        url = 'http://se.zhuangty.com:8000/curriculum/' + user.student_id
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        course_ids = []
        if response.status_code == 200:
            response_course = json.loads(response.content.decode())
            course_ids = list(set([c['courseid'] for c in response_course['classes']]))
        else:
            raise LogicError('Response Error in AssignmentList')
        result = []

        for course_id in course_ids:
            response_assignment = requests.post('http://se.zhuangty.com:8000/learnhelper/'
                                                + user.student_id + '/courses/' + course_id
                                                + '/assignments')
            if response_assignment.status_code == 200:
                result_assignment = json.loads(response_assignment.content.decode())

                for rc in response_course['classes']:
                    if rc['courseid'] == course_id:
                        course_name = rc['coursename']
                        break

                for assignment in result_assignment['assignments']:
                    assignment['coursename'] = course_name

                    assignment['processing'] = assignment['duedate'] > current_stamp()

                    assignment['startdate'] = stamp_to_localstr_date(assignment['startdate'])
                    assignment['evaluatingdate'] = stamp_to_localstr_date(assignment['evaluatingdate'])
                    assignment['read'] = ReadNoticeRecord.notice_name(assignment['title'], course_id) in read_assignments

                result += result_assignment['assignments']
            else:
                raise LogicError('Response Error in AssignmentList')

        length = len(result)
        result = sorted(result, key=lambda a: a['duedate'], reverse=True)[10 * (pagenum - 1): 10 * pagenum]
        unread = 0
        for index, r in enumerate(result):
            r['index'] = index + 1
            r['duedate'] = stamp_to_localstr_date(r['duedate'])
            r['detail'] = r['detail'].replace('\r\n', '</br>')
            r['comment'] = r['comment'].replace('\r\n', '</br>')
            if not r['read']:
                unread += 1

        return {
            'total': length,
            'assignments': result,
            'unread': unread
        }


class SlideList(APIView):

    def get(self):
        self.check_input('open_id', 'page')

        try:
            pagenum = int(self.input['page'])
        except:
            raise InputError('The given page should be int')

        try:
            user = User.get_by_openid(self.input['open_id'])
        except:
            raise LogicError('no such open_id')

        read_slides = user.get_read_slide_list()

        if user.student_id == '':
            raise LogicError('user not bound')

        url = 'http://se.zhuangty.com:8000/curriculum/' + user.student_id
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)

        if response.status_code == 200:
            response_course = json.loads(response.content.decode())
            course_ids = list(set([c['courseid'] for c in response_course['classes']]))

        result = []

        for course_id in course_ids:
            response_file = requests.post('http://se.zhuangty.com:8000/learnhelper/'
                                          + user.student_id + '/courses/' + course_id
                                          + '/documents')
            if response_file.status_code == 200:
                result_file = json.loads(response_file.content.decode())

                for rc in response_course['classes']:
                    if rc['courseid'] == course_id:
                        course_name = rc['coursename']
                        break

                for file in result_file['documents']:
                    file['coursename'] = course_name
                    file['read'] = ReadNoticeRecord.notice_name(file['title'], course_id) in read_slides

                result += result_file['documents']

            else:
                raise LogicError('Response Error')

        length = len(result)
        result = sorted(result, key=lambda a: a['updatingtime'], reverse=True)[10 * (pagenum - 1): 10 * pagenum]
        unread = 0
        for index, r in enumerate(result):
            r['index'] = index + 1
            r['updatingtime'] = stamp_to_localstr_date(r['updatingtime'])
            if not r['read']:
                unread += 1

        return {
            'total': length,
            'slides': result,
            'unread': unread
        }


class MeInfo(APIView):

    def get(self):
        self.check_input('open_id')

        try:
            user = User.get_by_openid(self.input['open_id'])
        except:
            raise LogicError('no such open_id')
        if user.student_id == '':
            raise LogicError('user not bound')
        url = 'http://se.zhuangty.com:8000/curriculum/' + user.student_id
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)

        if response.status_code == 200:
            response_course = json.loads(response.content.decode())
            course_ids = list(set([c['courseid'] for c in response_course['classes']]))

            dic = {
                'undergraduate': '本科就读',
                'master': '硕士',
                'doctor': '博士',
                'teacher': '教师'
            }

            return {
                'course_num': len(course_ids),
                'name': user.realname,
                'student_id': user.student_id,
                'status': dic[user.position],
                'school': user.department,
                'email': user.email,
                'course_list_url': get_redirect_url(event_urls['course_list'])
            }
        else:
            raise LogicError('response code 400')


class SearchCourse(APIView):
    def get(self):
        self.check_input('key', 'page')

        courses = []
        try:
            page_num = int(self.input['page'])
        except:
            raise InputError('the given page should be int')
        key = self.input['key']
        if key == '':
            courses = CourseForSearch.objects.all()
        else:
            courses = CourseForSearch.objects.filter(course_name=key)
            if len(courses) == 0:
                courses = CourseForSearch.fuzzy_search(key)

        res = [{
            'course_name': x.course_name,
            'course_id': x.course_id,
            'course_seq': x.course_seq,
            'school': x.school,
            'time': x.time,
            'week': x.week,
            'second': x.second,
            'intro': x.intro,
            'feature': x.feature,
            'score': x.score,
            'teacher': x.teacher,
            'year': x.year,
        } for x in courses][10 * (page_num - 1): 10 * page_num]

        for index, r in enumerate(res):
            r['index'] = index + 1
            r['course_seq'] = int(float(r['course_seq']))

        return {
            'total': len(courses),
            'search_result': res
        }


class CourseInfo(APIView):

    def get(self):
        self.check_input('open_id', 'course_id')
        try:
            user = User.get_by_openid(self.input['open_id'])
        except:
            raise LogicError("no such open_id")
        if user.student_id == '':
            raise LogicError('user not bound')
        url = 'http://se.zhuangty.com:8000/curriculum/' + user.student_id
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest'
        }

        result = {}
        response = requests.post(url, json=params)
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
                        result['teacher_email'] = ''
                        result['teacher_phone'] = ''
                        result['course_new_file'] = 0
                        result['course_unread_notice'] = 0
                        result['course_unsubmitted_operations'] = 0
                        for course in res['courses']:
                            if course['courseid'] == self.input['course_id']:
                                result['teacher_email'] = course['email']
                                result['teacher_phone'] = course['phone']
                                result['course_new_file'] = course['newfile']
                                result['course_unread_notice'] = course['unreadnotice']
                                result['course_unsubmitted_operations'] = course['unsubmittedoperations']
                                return {
                                    'info': result,
                                    'url': get_redirect_url(event_urls['communication'])
                                }
                        return {
                            'info': result,
                            'url': get_redirect_url(event_urls['communication'])
                        }
                    raise LogicError('Response Error')

            raise LogicError('No course')

        else:
            raise LogicError('Response Error')

    @classmethod
    def map_week(cls, week_list):
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


class CommentCreate(APIView):

    def post(self):
        self.check_input('content', 'score', 'course_id', 'course_name', 'open_id', 'isanonymous')

        params = self.input
        try:
            user = User.get_by_openid(params['open_id'])
        except:
            raise LogicError('no such open_id')
        if user.student_id == '':
            raise LogicError('user not bound')
        commenter_id = user.id
        try:
            score = int(params['score'])
        except:
            raise InputError('The given score should be int')
        if not 0 < score < 6:
            raise InputError('The given score is out of range')
        content = params['content']
        course_id = params['course_id']
        if params['isanonymous'] == 'true':
            isanonymous = 0
        else:
            isanonymous = 1
        create_time = current_stamp()
        course_name = params['course_name']
        Comment.objects.create(isanonymous = isanonymous, course_id=course_id, course_name=course_name, comment_time=create_time, commenter_id=commenter_id, content=content, score=score)


class CommentList(APIView):

    def get(self):
        self.check_input('open_id')
        try:
            user = User.get_by_openid(self.input['open_id'])
        except:
            raise LogicError('no such open_id')
        if user.student_id == '':
            raise LogicError('user not bound')
        all_comments = [{
                            'time': float(x.comment_time),
                            'content': x.content,
                            'id': x.id,
                            'real_name': x.get_commenter_name(),
                            'course_name': x.course_name,
                            'course_id': x.course_id,
                        }
                        for x in Comment.objects.all()]
        if 'course_id' in self.input:
            if 'end_id' in self.input:
                try:
                    id = int(self.input['end_id'])
                except:
                    raise InputError('The given id should be int')
                try:
                    end_time = float(Comment.objects.get(id=id).comment_time)
                except:
                    raise LogicError('no such id')
                comments = []
                for cmt in all_comments:
                    if cmt['time'] < end_time and cmt['course_id'] == self.input['course_id']:
                        comments.append(cmt)
                result = sorted(comments, key=lambda d: d['time'], reverse=True)
                length = len(result)
                if length > 10:
                    result = result[0:10]
            else:
                comments = []
                for cmt in all_comments:
                    if cmt['course_id'] == self.input['course_id']:
                        comments.append(cmt)
                result = sorted(comments, key=lambda d: d['time'], reverse=True)
                length = len(result)
                if length > 10:
                    result = result[0:10]
        else:
            if 'end_id' in self.input:
                try:
                    id = int(self.input['end_id'])
                except:
                    raise InputError('The given id should be int')
                try:
                    end_time = float(Comment.objects.get(id=id).comment_time)
                except:
                    raise LogicError('no such id')
                comments = []
                for cmt in all_comments:
                    if cmt['time'] < end_time:
                        comments.append(cmt)
                result = sorted(comments, key=lambda d: d['time'], reverse=True)
                length = len(result)
                if length > 10:
                    result = result[0:10]
            else:
                result = sorted(all_comments, key=lambda d: d['time'], reverse=True)
                length = len(result)
                if length > 10:
                    result = result[0:10]
        return result


class GetUserInfo(APIView):
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
        openid = result['openid']
        access_token = result['access_token']
        url2 = 'https://api.weixin.qq.com/sns/userinfo?access_token='
        url2 += access_token
        url2 += '&openid='
        url2 += openid
        url2 += '&lang=zh_CN'
        response = requests.get(url2)
        result = json.loads(response.content.decode())
        try:
            user = User.get_by_openid(openid)
            user.avatar_url = result['headimgurl']
            user.save()
        except:
            raise LogicError('can not get avatar')
        return {
            'open_id': openid
        }


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
        #this openid is defined by TX
        return {
            'open_id': result['openid']
        }


class GetJSSDK(APIView):

    def get(self):
        self.check_input('url')

        confirm = WechatConfirmation.get_or_create()
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
        self.check_input('open_id', 'id')
        try:
            user = User.get_by_openid(self.input['open_id'])
        except:
            raise LogicError('no such open_id')
        event_id_list = json.loads(user.event_list)
        event_list = sorted([Event.get_by_id(x) for x in event_id_list], key=lambda d: d.date)
        try:
            id = int(self.input['id'])
        except:
            raise InputError('The given id should be int')
        if 0 <= id < len(event_list):
            return {
                'name':event_list[id].name,
                'date': stamp_to_utcstr_date(float(event_list[id].date)),
                'content': event_list[id].content
            }
        raise InputError('The given id is out of range')

    def post(self):
        self.check_input('open_id', 'name', 'date', 'content', 'id')
        try:
            user = User.get_by_openid(self.input['open_id'])
        except:
            raise LogicError('no such open_id')
        event_id_list = json.loads(user.event_list)
        try:
            id = int(self.input['id'])
        except:
            raise InputError('The given id should be int')
        if 0 <= id < len(event_id_list):
            event = Event.get_by_id(event_id_list[id])
            event.name = self.input['name']
            try:
                event.date = utcstr_date_to_stamp(self.input['date'])
            except:
                raise InputError('incorrect given date')
            event.content = self.input['content']
            event.save()
            return {
                'id': id,
            }
        else:
            raise InputError('The given id is out of range')


class EventList(APIView):

    def get(self):
        self.check_input('open_id', 'mode')
        if self.input['mode'] == 'day':
            if 'date' not in self.input:
                date = date_today()
            else:
                try:
                    date = datetime.datetime.strptime(self.input['date'], '%Y-%m-%d') + datetime.timedelta(days = 1)
                except:
                    raise  InputError('incorrect given date')
            try:
                user = User.get_by_openid(self.input['open_id'])
            except:
                raise LogicError('no such open_id')
            event_id_list = json.loads(user.event_list)
            event_list = sorted([Event.get_by_id(x) for x in event_id_list], key=lambda d: d.date)
            result = []
            record = []
            count = 0
            for e in event_list:
                xsx = stamp_to_utcstr_date(float(e.date))
                if float(e.date) >= date.timestamp():
                    count += 1
                    e_date = stamp_to_utcstr_date(float(e.date))
                    if e_date in record:
                        result[len(result) - 1].append({
                            'id': user.search_event(e.id),
                            'name': e.name,
                            'date': e_date,
                            'content': e.content
                        })
                    elif count < 11:
                        record.append(e_date)
                        result.append([{
                            'id': user.search_event(e.id),
                            'name': e.name,
                            'date': e_date,
                            'content': e.content
                        }])
                    else:
                        break
            return {
                'events': result
            }
        elif self.input['mode'] == 'month':
            self.check_input('month')
            try:
                date = datetime.datetime.strptime(self.input['month'], '%Y-%m')
            except:
                raise InputError('incorrect given month')
            try:
                user = User.get_by_openid(self.input['open_id'])
            except:
                raise LogicError('no such open_id')
            event_id_list = json.loads(user.event_list)
            event_list = sorted([Event.get_by_id(x) for x in event_id_list], key=lambda d: d.date)
            result = []
            for e in event_list:
                if self.month_range(datetime.datetime.fromtimestamp(float(e.date)), date):
                    e_date = stamp_to_utcstr_date(float(e.date))
                    result.append({
                        'id': user.search_event(e.id),
                        'name': e.name,
                        'date': e_date,
                    })
            return result

    @classmethod
    def month_range(cls, date1, date2):
        if time.mktime(date1.timetuple()) >= time.mktime(date2.timetuple())\
                and date1.month == date2.month and date1.year == date2.year:
            return True
        else:
            return False


class EventCreate(APIView):

    def post(self):
        self.check_input('open_id', 'name', 'date', 'content')
        try:
            event = Event.objects.create(
                name = self.input['name'],
                date = datetime.datetime.strptime(self.input['date'], '%Y-%m-%d').timestamp(),
                content = self.input['content']
            )
        except:
            raise InputError('incorrect given date')
        try:
            id = User.get_by_openid(self.input['open_id']).add_event(event.id)
        except:
            raise LogicError('no such open_id')
        return {
            'id': id
        }


class EventDelete(APIView):

    def post(self):
        self.check_input('open_id', 'id')
        try:
            user = User.get_by_openid(self.input['open_id'])
        except:
            raise LogicError('no such open_id')
        try:
            user.del_event(int(self.input['id']))
        except:
            raise InputError('The given id is out of range')


class ReadNoticeRecord(APIView):

    def post(self):
        self.check_input('open_id', 'type', 'name', 'course_id')
        try:
            user = User.get_by_openid(self.input['open_id'])
        except:
            raise LogicError('no such open_id')
        name = self.notice_name(self.input['name'], self.input['course_id'])
        if self.input['type'] == '1':
            user.add_notice(name)
        elif self.input['type'] == '2':
            user.add_assignment(name)
        elif self.input['type'] == '3':
            user.add_slide(name)
        else:
            raise InputError('unknown type')


    @classmethod
    def notice_name(cls, name, course_id):
        if len(name) > 5:
            name = name[0:5]
        result = name + '&'
        result += course_id
        return result


class Communicate(APIView):

    def get(self):
        self.check_input('open_id', 'course_id')
        reply = Course.objects.get(course_id=self.input['course_id']).get_msg()
        msgs = reply['data']
        update_index = reply['index']
        answer = []
        for msg in msgs:
            user = User.objects.get(open_id=msg.sender_id)
            c = {
                'realname': user.realname,
                'avatar_url': user.avatar_url,
                'content': msg.content
            }
            answer.append(c)
        return {
            'update_index': update_index,
            'msgs': answer
        }

    def post(self):
        self.check_input('open_id', 'course_id', 'content')
        openid = self.input['open_id']
        courseid = self.input['course_id']
        content = self.input['content']
        Course.objects.get(course_id=courseid).add_msg(openid, content)
        return


class CommunicateNew(APIView):

    def post(self):
        self.check_input('open_id', 'course_id', 'index')
        openid = self.input['open_id']
        courseid = self.input['course_id']
        last_update = self.input['index']
        while True:
            course = Course.objects.get(course_id=courseid)
            if course.update_index > int(last_update):
                return
            time.sleep(2)


class CommunicateList(APIView):

    def get(self):
        self.check_input('open_id')
        try:
            user = User.get_by_openid(self.input['open_id'])
        except:
            raise LogicError("no such open_id")

        url = 'http://se.zhuangty.com:8000/learnhelper/' + user.student_id + '/courses'
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest'
        }
        result = {}
        response = requests.post(url, json=params)
        try:
            if response.status_code == 200:
                result_course = json.loads(response.content.decode())['courses']
                for index, c in enumerate(result_course):
                    c['index'] = index + 1
                return {
                    'courses': result_course,
                }
            else:
                raise LogicError('Response Error')
        except:
            raise LogicError('Response Error')
