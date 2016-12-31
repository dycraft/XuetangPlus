import json
from XuetangPlus.settings import event_urls, get_redirect_url
import requests
from django.test import TestCase
import datetime
from util.time import *
from wechat.views import CustomWeChatView
from wechat.handlers import ErrorHandler, DefaultHandler, HelpOrSubscribeHandler, UnbindOrUnsubscribeHandler, \
    AccountBindHandler, ViewPersonalInformationHandler, CourseSearchHandler, CourseListHandler, CommunicateHandler, \
    NoticePanelHandler, LibraryRemainsHandler, MyCalendarHandler, SchoolCalendarHandler, NavigationHandler, \
    RemindHandler
from wechat.models import User, Event, CourseForSearch, Comment, Course
from userpage.views import ReadNoticeRecord, CourseInfo

data_for_test = {
    'username': '2014013421',
    'password': 'xsx345997420QXX',
}

start_time = [
    '08:00',
    '09:50',
    '13:30',
    '15:20',
    '17:05',
    '19:20',
]


class ErrorHandlerTestCase(TestCase):
    fixtures = ['user.json']

    @classmethod
    def setUp(cls):
        cls.msg = {'ToUserName': '2', 'FromUserName': '1'}

    def test(self):
        user = User.get_by_openid('1')
        inst = ErrorHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T'))


class DefaultHandlerTestCase(TestCase):
    fixtures = ['user.json']

    @classmethod
    def setUp(cls):
        cls.msg = {'ToUserName': '2', 'FromUserName': '1'}

    def test(self):
        user = User.get_by_openid('1')
        inst = DefaultHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        inputStr = 'input string'
        self.assertEqual(inst.handle(inputStr), inst.reply_text('对不起，没有找到您需要的信息:(\n您查找的内容为(' + inputStr
                               + ')\n\n我们目前支持的功能包括帮助、解绑、绑定、我的信息、查找课程、我的课程、'
                                 '课程交流、通知面板、文图、我的日历、校历、导航、提醒'))


class HelpOrSubscribeHandlerTestCase(TestCase):
    fixtures = ['user.json']

    @classmethod
    def setUp(cls):
        cls.msg = {
            'ToUserName': '2',
            'FromUserName': '1',
            'MsgType': '',
            'Content': '',
            'Event': ''
        }

    def test_when_correct_text(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '帮助'
        user = User.get_by_openid('1')
        inst = HelpOrSubscribeHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_single_news({
            'Title': inst.get_message('help_title'),
            'Description': inst.get_message('help_description'),
            'Url': inst.url_help(),
            'PicUrl': inst.url_pic('/img/theme/help.png')
        }))
        self.msg['Content'] = 'help'
        inst = HelpOrSubscribeHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_single_news({
            'Title': inst.get_message('help_title'),
            'Description': inst.get_message('help_description'),
            'Url': inst.url_help(),
            'PicUrl': inst.url_pic('/img/theme/help.png')
        }))

    def test_when_correct_event(self):
        self.msg['MsgType'] = 'event'
        self.msg['Event'] = 'scan'
        user = User.get_by_openid('1')
        inst = HelpOrSubscribeHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_single_news({
            'Title': inst.get_message('help_title'),
            'Description': inst.get_message('help_description'),
            'Url': inst.url_help(),
            'PicUrl': inst.url_pic('/img/theme/help.png')
        }))
        self.msg['Event'] = 'subscribe'
        inst = HelpOrSubscribeHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_single_news({
            'Title': inst.get_message('help_title'),
            'Description': inst.get_message('help_description'),
            'Url': inst.url_help(),
            'PicUrl': inst.url_pic('/img/theme/help.png')
        }))

    def test_when_incorrect_text(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '123'
        user = User.get_by_openid('1')
        inst = HelpOrSubscribeHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)

    def test_when_incorrect_event(self):
        self.msg['MsgType'] = 'event'
        self.msg['Event'] = '123'
        user = User.get_by_openid('1')
        inst = HelpOrSubscribeHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)


class UnbindOrUnsubscribeHandlerTestCase(TestCase):
    fixtures = ['user.json']

    @classmethod
    def setUp(cls):
        cls.msg = {
            'ToUserName': '2',
            'FromUserName': '1',
            'MsgType': '',
            'Content': '',
            'Event': ''
        }

    def test_when_correct_text1(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '解绑'
        user = User.get_by_openid('1')
        inst = UnbindOrUnsubscribeHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text('您还未绑定'))

    def test_when_correct_text2(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '解绑'
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        user = User.get_by_openid('1')
        inst = UnbindOrUnsubscribeHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text(inst.get_message('account_unbind')))

    def test_when_correct_event1(self):
        self.msg['MsgType'] = 'event'
        self.msg['Event'] = 'unsubscribe'
        user = User.get_by_openid('1')
        inst = UnbindOrUnsubscribeHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text('您还未绑定'))

    def test_when_correct_event2(self):
        self.msg['MsgType'] = 'event'
        self.msg['Event'] = 'unsubscribe'
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        user = User.get_by_openid('1')
        inst = UnbindOrUnsubscribeHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text(inst.get_message('account_unbind')))

    def test_when_incorrect_text(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '123'
        user = User.get_by_openid('1')
        inst = UnbindOrUnsubscribeHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)

    def test_when_incorrect_event(self):
        self.msg['MsgType'] = 'event'
        self.msg['Event'] = '123'
        user = User.get_by_openid('1')
        inst = UnbindOrUnsubscribeHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)


class AccountBindHandlerTestCase(TestCase):
    fixtures = ['user.json']

    @classmethod
    def setUp(cls):
        cls.msg = {
            'ToUserName': '2',
            'FromUserName': '1',
            'MsgType': '',
            'Content': '',
            'Event': ''
        }

    def test_when_correct_text1(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '绑定'
        user = User.get_by_openid('1')
        inst = AccountBindHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text(inst.get_message('account_bind')))

    def test_when_correct_text2(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '绑定'
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        user = User.get_by_openid('1')
        inst = AccountBindHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text('您已经绑定学号' + user.student_id))

    def test_when_incorrect_text(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '123'
        user = User.get_by_openid('1')
        inst = AccountBindHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)


class ViewPersonalInformationHandlerTestCase(TestCase):
    fixtures = ['user.json']

    @classmethod
    def setUp(cls):
        cls.msg = {
            'ToUserName': '2',
            'FromUserName': '1',
            'MsgType': '',
            'Content': '',
            'Event': ''
        }

    def test_when_correct_text1(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '我的信息'
        user = User.get_by_openid('1')
        inst = ViewPersonalInformationHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text('请先进行绑定'))

    def test_when_correct_text2(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '我的信息'
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        user = User.get_by_openid('1')
        inst = ViewPersonalInformationHandler(CustomWeChatView, self.msg, user)
        dic = {
            'undergraduate': '本科就读',
            'master': '硕士',
            'doctor': '博士',
            'teacher': '教师'
        }
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text('姓名：' + user.realname + '\n'
                                                        + '学号：' + user.student_id + '\n'
                                                        + '学位：' + dic[user.position] + '\n'
                                                        + '院系：' + user.department + '\n'
                                                        + '邮箱：' + user.email + '\n'))

    def test_when_incorrect_text(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '123'
        user = User.get_by_openid('1')
        inst = ViewPersonalInformationHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)


class CourseSearchHandlerTestCase(TestCase):
    fixtures = ['user.json']

    @classmethod
    def setUp(cls):
        cls.msg = {
            'ToUserName': '2',
            'FromUserName': '1',
            'MsgType': '',
            'Content': '',
            'Event': ''
        }

    def test_when_correct_text1(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '查找课程'
        user = User.get_by_openid('1')
        inst = CourseSearchHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text('请先进行绑定'))

    def test_when_correct_text2(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '查找课程'
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        user = User.get_by_openid('1')
        inst = CourseSearchHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_single_news({
            'Title': '欢迎使用课程搜索',
            'Description': '在这里你可以方便的查询课程的信息',
            'Url': inst.url_course_search(),
            'PicUrl': inst.url_pic('/img/theme/search_course.png')
        }))

    def test_when_incorrect_text(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '123'
        user = User.get_by_openid('1')
        inst = CourseSearchHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)


class CourseListHandlerTestCase(TestCase):
    fixtures = ['user.json']

    @classmethod
    def setUp(cls):
        cls.msg = {
            'ToUserName': '2',
            'FromUserName': '1',
            'MsgType': '',
            'Content': '',
            'Event': ''
        }

    def test_when_correct_text1(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '我的课程'
        user = User.get_by_openid('1')
        inst = CourseListHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text('请先进行绑定'))

    def test_when_correct_text2(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '我的课程'
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        user = User.get_by_openid('1')
        inst = CourseListHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_single_news({
            'Title': '欢迎查看您的课程',
            'Description': '点击查看课程列表',
            'Url': inst.url_my_course(),
            'PicUrl': inst.url_pic('/img/theme/my_course.png')
        }))

    def test_when_incorrect_text(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '123'
        user = User.get_by_openid('1')
        inst = CourseListHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)


class CommunicateHandlerTestCase(TestCase):
    fixtures = ['user.json']

    @classmethod
    def setUp(cls):
        cls.msg = {
            'ToUserName': '2',
            'FromUserName': '1',
            'MsgType': '',
            'Content': '',
            'Event': ''
        }

    def test_when_correct_text1(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '课程交流'
        user = User.get_by_openid('1')
        inst = CommunicateHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text('请先进行绑定'))

    def test_when_correct_text2(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '课程交流'
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        user = User.get_by_openid('1')
        inst = CommunicateHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_single_news({
            'Title': '欢迎使用课程交流',
            'Description': '在交流中学习',
            'Url': inst.url_communication(),
            'PicUrl': inst.url_pic('/img/theme/communication.png')
        }))

    def test_when_incorrect_text(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '123'
        user = User.get_by_openid('1')
        inst = CommunicateHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)


class NoticePanelHandlerTestCase(TestCase):
    fixtures = ['user.json']

    @classmethod
    def setUp(cls):
        cls.msg = {
            'ToUserName': '2',
            'FromUserName': '1',
            'MsgType': '',
            'Content': '',
            'Event': ''
        }

    def test_when_correct_text1(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '通知面板'
        user = User.get_by_openid('1')
        inst = NoticePanelHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text('请先进行绑定'))

    def test_when_correct_text2(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '通知面板'
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        user = User.get_by_openid('1')
        inst = NoticePanelHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_single_news({
            'Title': '欢迎使用通知面板',
            'Description': '查看各个课程的公告与作业',
            'Url': inst.url_notification(),
            'PicUrl': inst.url_pic('/img/theme/notification.png')
        }))

    def test_when_incorrect_text(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '123'
        user = User.get_by_openid('1')
        inst = NoticePanelHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)


class LibraryRemainsHandlerTestCase(TestCase):
    fixtures = ['user.json']

    @classmethod
    def setUp(cls):
        cls.msg = {
            'ToUserName': '2',
            'FromUserName': '1',
            'MsgType': '',
            'Content': '',
            'Event': ''
        }

    def test_when_correct_text(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '文图'
        user = User.get_by_openid('1')
        inst = LibraryRemainsHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        response = requests.post('http://se.zhuangty.com:8000/library/hs')
        if response.status_code == 200:
            res = json.loads(response.content.decode())
            reply = "文图剩余座位\n"
            reply += '\n'.join([area['name'] + '：' + str(area['left'])
                                + '/' + str(area['left'] + area['used']) for area in res['areas']])
            self.assertEqual(inst.handle(), inst.reply_text(reply))
        else:
            self.assertEqual(inst.handle(), inst.reply_text('很抱歉，现在无法查询到剩余座位，请稍后再试。'))

    def test_when_correct_event_click(self):
        self.msg['MsgType'] = 'event'
        self.msg['Event'] = 'CLICK'
        self.msg['EventKey'] = 'LIFE_LIBRARY'
        user = User.get_by_openid('1')
        inst = LibraryRemainsHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        response = requests.post('http://se.zhuangty.com:8000/library/hs')
        if response.status_code == 200:
            res = json.loads(response.content.decode())
            reply = "文图剩余座位\n"
            reply += '\n'.join([area['name'] + '：' + str(area['left'])
                                + '/' + str(area['left'] + area['used']) for area in res['areas']])
            self.assertEqual(inst.handle(), inst.reply_text(reply))
        else:
            self.assertEqual(inst.handle(), inst.reply_text('很抱歉，现在无法查询到剩余座位，请稍后再试。'))

    def test_when_incorrect_text(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '123'
        user = User.get_by_openid('1')
        inst = LibraryRemainsHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)

    def test_when_incorrect_event_click(self):
        self.msg['MsgType'] = 'event'
        self.msg['Event'] = 'CLICK'
        self.msg['EventKey'] = '123'
        user = User.get_by_openid('1')
        inst = LibraryRemainsHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)


class MyCalendarHandlerTestCase(TestCase):
    fixtures = ['user.json']

    @classmethod
    def setUp(cls):
        cls.msg = {
            'ToUserName': '2',
            'FromUserName': '1',
            'MsgType': '',
            'Content': '',
            'Event': ''
        }

    def test_when_correct_text1(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '我的日历'
        user = User.get_by_openid('1')
        inst = MyCalendarHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text('请先进行绑定'))

    def test_when_correct_text2(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '我的日历'
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        user = User.get_by_openid('1')
        inst = MyCalendarHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_single_news({
            'Title': '欢迎使用个人日历',
            'Description': '在这里你可以方便查看和管理你的日程',
            'Url': inst.url_my_calendar(),
            'PicUrl': inst.url_pic('/img/theme/calendar.png')
        }))

    def test_when_incorrect_text(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '123'
        user = User.get_by_openid('1')
        inst = MyCalendarHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)


class SchoolCalendarHandlerTestCase(TestCase):
    fixtures = ['user.json']

    @classmethod
    def setUp(cls):
        cls.msg = {
            'ToUserName': '2',
            'FromUserName': '1',
            'MsgType': '',
            'Content': '',
            'Event': ''
        }

    def test_when_correct_text(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '校历'
        user = User.get_by_openid('1')
        inst = SchoolCalendarHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        response = requests.post('http://se.zhuangty.com:8000/events')
        if response.status_code == 200:
            res = json.loads(response.content.decode())
            reply = '\n'.join(['距 ' + event['name'] + (' 开始' if event['status'] == 'begin' else ' 结束')
                               + '还有' + str(event['remainingdays']) + '天' for event in res['events']])
            self.assertEqual(inst.handle(), inst.reply_text(reply))
        else:
            self.assertEqual(inst.handle(), inst.reply_text('很抱歉，现在无法查询到校历资讯，请稍后再试。'))

    def test_when_correct_event_click(self):
        self.msg['MsgType'] = 'event'
        self.msg['Event'] = 'CLICK'
        self.msg['EventKey'] = 'LIFE_SCHOOL_CALENDAR'
        user = User.get_by_openid('1')
        inst = SchoolCalendarHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        response = requests.post('http://se.zhuangty.com:8000/events')
        if response.status_code == 200:
            res = json.loads(response.content.decode())
            reply = '\n'.join(['距 ' + event['name'] + (' 开始' if event['status'] == 'begin' else ' 结束')
                               + '还有' + str(event['remainingdays']) + '天' for event in res['events']])
            self.assertEqual(inst.handle(), inst.reply_text(reply))
        else:
            self.assertEqual(inst.handle(), inst.reply_text('很抱歉，现在无法查询到校历资讯，请稍后再试。'))

    def test_when_incorrect_text(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '123'
        user = User.get_by_openid('1')
        inst = SchoolCalendarHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)

    def test_when_incorrect_event_click(self):
        self.msg['MsgType'] = 'event'
        self.msg['Event'] = 'CLICK'
        self.msg['EventKey'] = '123'
        user = User.get_by_openid('1')
        inst = SchoolCalendarHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)


class NavigationHandlerTestCase(TestCase):
    fixtures = ['user.json']

    @classmethod
    def setUp(cls):
        cls.msg = {
            'ToUserName': '2',
            'FromUserName': '1',
            'MsgType': '',
            'Content': '',
            'Event': ''
        }

    def test_when_correct_text(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '导航'
        user = User.get_by_openid('1')
        inst = NavigationHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_single_news({
            'Title': '欢迎使用校园导航',
            'Description': '输入地点进行导航',
            'Url': inst.url_navigation(),
            'PicUrl': inst.url_pic('/img/theme/navigation.png')
        }))

    def test_when_correct_event_click(self):
        self.msg['MsgType'] = 'event'
        self.msg['Event'] = 'CLICK'
        self.msg['EventKey'] = 'LIFE_NAVIGATION'
        user = User.get_by_openid('1')
        inst = NavigationHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_single_news({
            'Title': '欢迎使用校园导航',
            'Description': '输入地点进行导航',
            'Url': inst.url_navigation(),
            'PicUrl': inst.url_pic('/img/theme/navigation.png')
        }))

    def test_when_incorrect_text(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '123'
        user = User.get_by_openid('1')
        inst = NavigationHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)

    def test_when_incorrect_event_click(self):
        self.msg['MsgType'] = 'event'
        self.msg['Event'] = 'CLICK'
        self.msg['EventKey'] = '123'
        user = User.get_by_openid('1')
        inst = NavigationHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)


class RemindHandlerTestCase(TestCase):
    fixtures = ['user.json']

    @classmethod
    def setUp(cls):
        cls.msg = {
            'ToUserName': '2',
            'FromUserName': '1',
            'MsgType': '',
            'Content': '',
            'Event': ''
        }

    def test_when_correct_text1(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '提醒'
        user = User.get_by_openid('1')
        inst = RemindHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text('请先进行绑定'))

    def test_when_correct_text2(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '提醒'
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        user = User.get_by_openid('1')
        inst = RemindHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text('欢迎使用提醒功能'))

    def test_when_incorrect_text(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '123'
        user = User.get_by_openid('1')
        inst = NavigationHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), False)


class AccountBindViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_get_correct_input(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        response = self.client.get('/api/welcome/account_bind', {'open_id': 1})
        res = response.json()
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], {'student_id': data_for_test['username']})

    def test_get_incorrect_input1(self):
        response = self.client.get('/api/welcome/account_bind', {'sth': 'sth'})
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "open_id" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input2(self):
        response = self.client.get('/api/welcome/account_bind', {'open_id': 2})
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'no such open_id')
        self.assertEqual(res['data'], None)

    def test_post_correct_input(self):
        response = self.client.post('/api/welcome/account_bind',
                                    {
                                        'open_id': '1',
                                        'student_id': data_for_test['username'],
                                        'password': data_for_test['password']
                                    })
        res = response.json()
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input1(self):
        response = self.client.post('/api/welcome/account_bind',
                                    {
                                        'student_id': data_for_test['username'],
                                        'password': data_for_test['password'],
                                    })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "open_id" required')
        self.assertEqual(res['data'], None)
        response = self.client.post('/api/welcome/account_bind',
                                    {
                                        'open_id': '1',
                                        'password': data_for_test['password'],
                                    })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "student_id" required')
        self.assertEqual(res['data'], None)
        response = self.client.post('/api/welcome/account_bind',
                                    {
                                        'open_id': '1',
                                        'student_id': data_for_test['username'],
                                    })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "password" required')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input2(self):
        response = self.client.post('/api/welcome/account_bind',
                                    {
                                        'open_id': '1',
                                        'student_id': '',
                                        'password': data_for_test['password'],
                                    })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Empty student_id or password.')
        self.assertEqual(res['data'], None)
        response = self.client.post('/api/welcome/account_bind',
                                    {
                                        'open_id': '1',
                                        'student_id': data_for_test['username'],
                                        'password': '',
                                    })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Empty student_id or password.')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input3(self):
        response = self.client.post('/api/welcome/account_bind',
                                    {
                                        'open_id': '1',
                                        'student_id': data_for_test['username'] + '111',
                                        'password': data_for_test['password'],
                                    })
        res = response.json()
        self.assertEqual(res['code'], 3)
        self.assertEqual(res['msg'], 'Wrong username or password.')
        self.assertEqual(res['data'], None)
        response = self.client.post('/api/welcome/account_bind',
                                    {
                                        'open_id': '1',
                                        'student_id': data_for_test['username'],
                                        'password': data_for_test['password'] + '111',
                                    })
        res = response.json()
        self.assertEqual(res['code'], 3)
        self.assertEqual(res['msg'], 'Wrong username or password.')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input4(self):
        response = self.client.post('/api/welcome/account_bind',
                                    {
                                        'open_id': '2',
                                        'student_id': data_for_test['username'],
                                        'password': data_for_test['password'],
                                    })
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'no such open_id')
        self.assertEqual(res['data'], None)


class CheckBindViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_get_correct_input1(self):
        response = self.client.get('/api/welcome/check_bind', {'open_id': 1})
        res = response.json()
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], {'bind': False})

    def test_get_correct_input2(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        response = self.client.get('/api/welcome/check_bind', {'open_id': 1})
        res = response.json()
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], {
            'bind': True,
            'student_id': data_for_test['username']
        })

    def test_get_incorrect_input1(self):
        response = self.client.get('/api/welcome/check_bind', {})
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "open_id" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input2(self):
        response = self.client.get('/api/welcome/check_bind', {'open_id': 2})
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'no such open_id')
        self.assertEqual(res['data'], None)


class UnBindViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_post_correct_input(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password'],
                         })
        response = self.client.post('/api/welcome/unbind', {'open_id': 1})
        res = response.json()
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input1(self):
        response = self.client.post('/api/welcome/unbind', {'open_id': 1})
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'user not bound')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input2(self):
        response = self.client.post('/api/welcome/unbind', {'sth': 'sth'})
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "open_id" required')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input3(self):
        response = self.client.post('/api/welcome/unbind', {'open_id': 2})
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'no such open_id')
        self.assertEqual(res['data'], None)


class CourseListViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_get_correct_input(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password'],
                         })
        response = self.client.get('/api/learn/course_list', {'open_id': 1})
        res = response.json()
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
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
            self.assertEqual(res['code'], 0)
            self.assertEqual(res['msg'], '')
            self.assertEqual(res['data'], {'classes': classes})
        else:
            self.assertEqual(res['code'], 2)
            self.assertEqual(res['msg'], 'Response error')
            self.assertEqual(res['data'], None)

    def test_get_incorrect_input1(self):
        response = self.client.get('/api/learn/course_list', {'sth': 'sth'})
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "open_id" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input2(self):
        response = self.client.get('/api/learn/course_list', {'open_id': 2})
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'no such open_id')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input3(self):
        response = self.client.get('/api/learn/course_list', {'open_id': 1})
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'unbind user')
        self.assertEqual(res['data'], None)


class NoticeListViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_get_correct_input(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        page_num = 1
        response = self.client.get('/api/learn/notice_panel/notice',
                                   {
                                       'open_id': 1,
                                       'page': page_num,
                                   })
        res = response.json()
        user = User.get_by_openid(1)
        read_notices = user.get_read_notice_list()

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
            self.assertEqual(res['code'], 2)
            self.assertEqual(res['msg'], 'Response Error in NoticeList')
            self.assertEqual(res['data'], None)

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
                self.assertEqual(res['code'], 2)
                self.assertEqual(res['msg'], 'Response Error in NoticeList')
                self.assertEqual(res['data'], None)

        length = len(result)
        result = sorted(result, key=lambda n: n['publishtime'], reverse=True)[10 * (page_num - 1): 10 * page_num]
        unread = 0
        for index, r in enumerate(result):
            r['index'] = index + 1
            r['title'] = r['title'].replace('&nbsp;', '')
            r['publishtime'] = stamp_to_localstr_date(r['publishtime'])
            r['content'] = r['content'].replace('\r\n', '</br>')
            if not r['read']:
                unread += 1

        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], {
            'total': length,
            'notices': result,
            'unread': unread
        })

    def test_get_incorrect_input1(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        page_num = 1
        response = self.client.get('/api/learn/notice_panel/notice',
                                   {
                                       'page': page_num,
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "open_id" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input2(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        page_num = 1
        response = self.client.get('/api/learn/notice_panel/notice',
                                   {
                                       'open_id': 1,
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "page" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input3(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        page_num = 1
        response = self.client.get('/api/learn/notice_panel/notice',
                                   {
                                       'open_id': 2,
                                       'page': page_num,
                                   })
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'no such open_id')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input4(self):
        page_num = 1
        response = self.client.get('/api/learn/notice_panel/notice',
                                   {
                                       'open_id': 1,
                                       'page': page_num,
                                   })
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'user not bound')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input5(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        response = self.client.get('/api/learn/notice_panel/notice',
                                   {
                                       'open_id': 1,
                                       'page': 1.3,
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given page should be int')
        self.assertEqual(res['data'], None)


class AssignmentListViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_get_correct_input(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        page_num = 1
        response = self.client.get('/api/learn/notice_panel/assignment',
                                   {
                                       'open_id': 1,
                                       'page': page_num,
                                   })
        res = response.json()
        user = User.get_by_openid(1)
        read_assignments = user.get_read_assignment_list()

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
            self.assertEqual(res['code'], 2)
            self.assertEqual(res['msg'], 'Response Error in AssignmentList')
            self.assertEqual(res['data'], None)

        result = []

        for course_id in course_ids:
            response_assignment = requests.post('http://se.zhuangty.com:8000/learnhelper/'
                                                + user.student_id + '/courses/' + course_id
                                                + '/assignments')
            if response_assignment.status_code == 200:
                result_assignment = json.loads(response_assignment.content.decode())
                course_name = ''
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
                self.assertEqual(res['code'], 2)
                self.assertEqual(res['msg'], 'Response Error in AssignmentList')
                self.assertEqual(res['data'], None)

        length = len(result)
        result = sorted(result, key=lambda a: a['duedate'], reverse=True)[10 * (page_num - 1): 10 * page_num]
        unread = 0
        for index, r in enumerate(result):
            r['index'] = index + 1
            r['duedate'] = stamp_to_localstr_date(r['duedate'])
            r['detail'] = r['detail'].replace('\r\n', '</br>')
            r['comment'] = r['comment'].replace('\r\n', '</br>')
            if not r['read']:
                unread += 1

        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], {
            'total': length,
            'assignments': result,
            'unread': unread
        })

    def test_get_incorrect_input1(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        page_num = 1
        response = self.client.get('/api/learn/notice_panel/assignment',
                                   {
                                       'page': page_num,
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "open_id" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input2(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        page_num = 1
        response = self.client.get('/api/learn/notice_panel/assignment',
                                   {
                                       'open_id': 1,
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "page" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input3(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        page_num = 1
        response = self.client.get('/api/learn/notice_panel/assignment',
                                   {
                                       'open_id': 2,
                                       'page': page_num,
                                   })
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'no such open_id')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input4(self):
        page_num = 1
        response = self.client.get('/api/learn/notice_panel/assignment',
                                   {
                                       'open_id': 1,
                                       'page': page_num,
                                   })
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'user not bound')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input5(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        response = self.client.get('/api/learn/notice_panel/assignment',
                                   {
                                       'open_id': 1,
                                       'page': 1.3,
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given page should be int')
        self.assertEqual(res['data'], None)


class SlideListViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_get_correct_input(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        page_num = 1
        response = self.client.get('/api/learn/notice_panel/slide',
                                   {
                                       'open_id': 1,
                                       'page': page_num,
                                   })
        res = response.json()
        user = User.get_by_openid(1)
        read_slides = user.get_read_slide_list()

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
            self.assertEqual(res['code'], 2)
            self.assertEqual(res['msg'], 'Response Error in SlideList')
            self.assertEqual(res['data'], None)

        result = []

        for course_id in course_ids:
            response_file = requests.post('http://se.zhuangty.com:8000/learnhelper/'
                                          + user.student_id + '/courses/' + course_id
                                          + '/documents')
            if response_file.status_code == 200:
                result_file = json.loads(response_file.content.decode())

                course_name = ''
                for rc in response_course['classes']:
                    if rc['courseid'] == course_id:
                        course_name = rc['coursename']
                        break

                for file in result_file['documents']:
                    file['coursename'] = course_name
                    file['read'] = ReadNoticeRecord.notice_name(file['title'], course_id) in read_slides

                result += result_file['documents']

            else:
                self.assertEqual(res['code'], 2)
                self.assertEqual(res['msg'], 'Response Error in SlideList')
                self.assertEqual(res['data'], None)

        length = len(result)
        result = sorted(result, key=lambda a: a['updatingtime'], reverse=True)[10 * (page_num - 1): 10 * page_num]
        unread = 0
        for index, r in enumerate(result):
            r['index'] = index + 1
            r['updatingtime'] = stamp_to_localstr_date(r['updatingtime'])
            if not r['read']:
                unread += 1

        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], {
            'total': length,
            'slides': result,
            'unread': unread
        })

    def test_get_incorrect_input1(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        page_num = 1
        response = self.client.get('/api/learn/notice_panel/slide',
                                   {
                                       'page': page_num,
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "open_id" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input2(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        page_num = 1
        response = self.client.get('/api/learn/notice_panel/slide',
                                   {
                                       'open_id': 1,
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "page" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input3(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        page_num = 1
        response = self.client.get('/api/learn/notice_panel/slide',
                                   {
                                       'open_id': 2,
                                       'page': page_num,
                                   })
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'no such open_id')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input4(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        response = self.client.get('/api/learn/notice_panel/slide',
                                   {
                                       'open_id': 1,
                                       'page': 1.3,
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given page should be int')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input5(self):
        page_num = 1
        response = self.client.get('/api/learn/notice_panel/slide',
                                   {
                                       'open_id': 1,
                                       'page': page_num,
                                   })
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'user not bound')
        self.assertEqual(res['data'], None)


class MeInfoViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_get_correct_input(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password'],
                         })
        response = self.client.get('/api/me/info',{'open_id': 1})
        res = response.json()
        user = User.get_by_openid(1)
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

            self.assertNotEqual(res['code'], 1)
            self.assertEqual(res['msg'], '')
            self.assertEqual(res['data'], {
                'course_num': len(course_ids),
                'name': user.realname,
                'student_id': user.student_id,
                'status': dic[user.position],
                'school': user.department,
                'email': user.email,
                'course_list_url': get_redirect_url(event_urls['course_list'])
            })
        else:
            self.assertEqual(res['code'], 0)
            self.assertEqual(res['msg'], '')
            self.assertEqual(res['data'], None)

    def test_get_incorrect_input1(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password'],
                         })
        response = self.client.get('/api/me/info',{'openid': 1})
        res = response.json()
        self.assertNotEqual(res['code'], 0)
        self.assertEqual(res['msg'], 'Field "open_id" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input2(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password'],
                         })
        response = self.client.get('/api/me/info',{'open_id': 2})
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'no such open_id')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input3(self):
        response = self.client.get('/api/me/info',{'open_id': 1})
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'user not bound')
        self.assertEqual(res['data'], None)


class SearchCourseViewTestCase(TestCase):
    fixtures = ['user.json']

    @classmethod
    def setUp(cls):
        CourseForSearch.objects.all().delete()
        course_data = json.load(open('./static/course/course.json', 'r'))

        length = len(course_data)
        for index, c in enumerate(course_data):
            new_course = CourseForSearch.objects.create()
            if c['course_name'] == '':
                new_course.delete()
                continue
            new_course.course_name = c['course_name']
            new_course.course_seq = c['course_seq']
            new_course.score = c['score']
            new_course.feature = c['feature']
            new_course.intro = c['intro']
            new_course.time = c['time']
            new_course.second = c['second']
            new_course.school = c['school']
            new_course.teacher = c['teacher']
            new_course.course_id = c['course_id']
            new_course.week = c['week']
            new_course.year = c['year']
            new_course.save()

    def test_get_correct_input(self):
        key = '工程'
        response = self.client.get('/api/learn/search_course',
                                   {
                                       'key': key,
                                       'page': '1',
                                   })
        res = response.json()
        courses = []
        page_num = 1
        courses = CourseForSearch.objects.filter(course_name=key)
        if len(courses) == 0:
            courses = CourseForSearch.fuzzy_search(key)


        result = [{
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

        for index, r in enumerate(result):
            r['index'] = index + 1
            r['course_seq'] = int(float(r['course_seq']))

        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], {
            'total': len(courses),
            'search_result': result,
        })

    def test_get_incorrect_input1(self):
        key = '工程'
        response = self.client.get('/api/learn/search_course',
                                   {
                                       'key': key,
                                       'page': '1.5',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'the given page should be int')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input2(self):
        response = self.client.get('/api/learn/search_course',
                                   {
                                       'page': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "key" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input3(self):
        response = self.client.get('/api/learn/search_course',
                                   {
                                       'key': '工程',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "page" required')
        self.assertEqual(res['data'], None)


class CourseInfoViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_get_correct_input(self):
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            self.client.post('/api/welcome/account_bind',
                             {
                                 'open_id': '1',
                                 'student_id': data_for_test['username'],
                                 'password': data_for_test['password'],
                             })
            response = self.client.get('/api/course/information',
                                       {
                                           'open_id': 1,
                                           'course_id': course_id,
                                       })
            res = response.json()
            user = User.get_by_openid(1)
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
                    if course['courseid'] == course_id:
                        result = course
                        result['course_day'] = course['time'][0]
                        result['course_time'] = start_time[course['time'][1] - 1]
                        result['course_week'] = CourseInfo.map_week(course['week'])

                        response = requests.post(
                            'http://se.zhuangty.com:8000/learnhelper/' + user.student_id + '/courses')
                        if response.status_code == 200:
                            re = json.loads(response.content.decode())
                            result['teacher_email'] = ''
                            result['teacher_phone'] = ''
                            result['course_new_file'] = 0
                            result['course_unread_notice'] = 0
                            result['course_unsubmitted_operations'] = 0
                            for course in re['courses']:
                                if course['courseid'] == course_id:
                                    result['teacher_email'] = course['email']
                                    result['teacher_phone'] = course['phone']
                                    result['course_new_file'] = course['newfile']
                                    result['course_unread_notice'] = course['unreadnotice']
                                    result['course_unsubmitted_operations'] = course['unsubmittedoperations']
                                    self.assertEqual(res['code'], 0)
                                    self.assertEqual(res['msg'], '')
                                    self.assertEqual(res['data'], {
                                        'info': result,
                                        'url': get_redirect_url(event_urls['communication']),
                                    })
                                    return

                            self.assertEqual(res['code'], 0)
                            self.assertEqual(res['msg'], '')
                            self.assertEqual(res['data'], {
                                'info': result,
                                'url': get_redirect_url(event_urls['communication']),
                            })
                            return
                        else:
                            self.assertEqual(res['code'], 2)
                            self.assertEqual(res['msg'], 'Response Error')
                            self.assertEqual(res['data'], None)
                            return

                self.assertEqual(res['code'], 2)
                self.assertEqual(res['msg'], 'No course')
                self.assertEqual(res['data'], None)
                return
            else:
                self.assertEqual(res['code'], 2)
                self.assertEqual(res['msg'], 'Response Error')
                self.assertEqual(res['data'], None)
                return

    def test_get_incorrect_input1(self):
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            self.client.post('/api/welcome/account_bind',
                             {
                                 'open_id': '1',
                                 'student_id': data_for_test['username'],
                                 'password': data_for_test['password'],
                             })
            response = self.client.get('/api/course/information',
                                       {
                                           'course_id': course_id,
                                       })
            res = response.json()
            self.assertEqual(res['code'], 1)
            self.assertEqual(res['msg'], 'Field "open_id" required')
            self.assertEqual(res['data'], None)

    def test_get_incorrect_input2(self):
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            self.client.post('/api/welcome/account_bind',
                             {
                                 'open_id': '1',
                                 'student_id': data_for_test['username'],
                                 'password': data_for_test['password'],
                             })
            response = self.client.get('/api/course/information',
                                       {
                                           'open_id': 1,
                                       })
            res = response.json()
            self.assertEqual(res['code'], 1)
            self.assertEqual(res['msg'], 'Field "course_id" required')
            self.assertEqual(res['data'], None)

    def test_get_incorrect_input3(self):
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            self.client.post('/api/welcome/account_bind',
                             {
                                 'open_id': '1',
                                 'student_id': data_for_test['username'],
                                 'password': data_for_test['password'],
                             })
            response = self.client.get('/api/course/information',
                                       {
                                           'open_id': 2,
                                           'course_id': course_id,
                                       })
            res = response.json()
            self.assertEqual(res['code'], 2)
            self.assertEqual(res['msg'], 'no such open_id')
            self.assertEqual(res['data'], None)

    def test_get_incorrect_input4(self):
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            response = self.client.get('/api/course/information',
                                       {
                                           'open_id': 1,
                                           'course_id': course_id,
                                       })
            res = response.json()
            self.assertEqual(res['code'], 2)
            self.assertEqual(res['msg'], 'user not bound')
            self.assertEqual(res['data'], None)


class CommentCreateViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_post_correct_input(self):
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            self.client.post('/api/welcome/account_bind',
                             {
                                 'open_id': '1',
                                 'student_id': data_for_test['username'],
                                 'password': data_for_test['password'],
                             })
            response = self.client.post('/api/course/comment/create',
                                        {
                                            'open_id': 1,
                                            'score': 1,
                                            'content': 'content',
                                            'isanonymous': 'true',
                                            'course_name': course_name,
                                            'course_id': course_id,
                                        })
            res = response.json()

            self.assertEqual(res['code'], 0)
            self.assertEqual(res['msg'], '')
            self.assertEqual(res['data'], None)

    def test_post_incorrect_input1(self):
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            self.client.post('/api/welcome/account_bind',
                             {
                                 'open_id': '1',
                                 'student_id': data_for_test['username'],
                                 'password': data_for_test['password'],
                             })
            response = self.client.post('/api/course/comment/create',
                                        {
                                            'score': 1,
                                            'content': 'content',
                                            'isanonymous': 'true',
                                            'course_name': course_name,
                                            'course_id': course_id,
                                        })
            res = response.json()

            self.assertEqual(res['code'], 1)
            self.assertEqual(res['msg'], 'Field "open_id" required')
            self.assertEqual(res['data'], None)

    def test_post_incorrect_input2(self):
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            self.client.post('/api/welcome/account_bind',
                             {
                                 'open_id': '1',
                                 'student_id': data_for_test['username'],
                                 'password': data_for_test['password'],
                             })
            response = self.client.post('/api/course/comment/create',
                                        {
                                            'open_id': 1,
                                            'content': 'content',
                                            'isanonymous': 'true',
                                            'course_name': course_name,
                                            'course_id': course_id,
                                        })
            res = response.json()

            self.assertEqual(res['code'], 1)
            self.assertEqual(res['msg'], 'Field "score" required')
            self.assertEqual(res['data'], None)

    def test_post_incorrect_input3(self):
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            self.client.post('/api/welcome/account_bind',
                             {
                                 'open_id': '1',
                                 'student_id': data_for_test['username'],
                                 'password': data_for_test['password'],
                             })
            response = self.client.post('/api/course/comment/create',
                                        {
                                            'open_id': 1,
                                            'score': 1,
                                            'isanonymous': 'true',
                                            'course_name': course_name,
                                            'course_id': course_id,
                                        })
            res = response.json()

            self.assertEqual(res['code'], 1)
            self.assertEqual(res['msg'], 'Field "content" required')
            self.assertEqual(res['data'], None)

    def test_post_incorrect_input4(self):
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            self.client.post('/api/welcome/account_bind',
                             {
                                 'open_id': '1',
                                 'student_id': data_for_test['username'],
                                 'password': data_for_test['password'],
                             })
            response = self.client.post('/api/course/comment/create',
                                        {
                                            'open_id': 1,
                                            'score': 1,
                                            'content': 'content',
                                            'course_name': course_name,
                                            'course_id': course_id,
                                        })
            res = response.json()

            self.assertEqual(res['code'], 1)
            self.assertEqual(res['msg'], 'Field "isanonymous" required')
            self.assertEqual(res['data'], None)

    def test_post_incorrect_input5(self):
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            self.client.post('/api/welcome/account_bind',
                             {
                                 'open_id': '1',
                                 'student_id': data_for_test['username'],
                                 'password': data_for_test['password'],
                             })
            response = self.client.post('/api/course/comment/create',
                                        {
                                            'open_id': 1,
                                            'score': 1,
                                            'content': 'content',
                                            'isanonymous': 'true',
                                            'course_id': course_id,
                                        })
            res = response.json()

            self.assertEqual(res['code'], 1)
            self.assertEqual(res['msg'], 'Field "course_name" required')
            self.assertEqual(res['data'], None)

    def test_post_incorrect_input6(self):
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            self.client.post('/api/welcome/account_bind',
                             {
                                 'open_id': '1',
                                 'student_id': data_for_test['username'],
                                 'password': data_for_test['password'],
                             })
            response = self.client.post('/api/course/comment/create',
                                        {
                                            'open_id': 1,
                                            'score': 1,
                                            'content': 'content',
                                            'isanonymous': 'true',
                                            'course_name': course_name,
                                        })
            res = response.json()

            self.assertEqual(res['code'], 1)
            self.assertEqual(res['msg'], 'Field "course_id" required')
            self.assertEqual(res['data'], None)

    def test_post_incorrect_input7(self):
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            self.client.post('/api/welcome/account_bind',
                             {
                                 'open_id': '1',
                                 'student_id': data_for_test['username'],
                                 'password': data_for_test['password'],
                             })
            response = self.client.post('/api/course/comment/create',
                                        {
                                            'open_id': 2,
                                            'score': 1,
                                            'content': 'content',
                                            'isanonymous': 'true',
                                            'course_name': course_name,
                                            'course_id': course_id,
                                        })
            res = response.json()

            self.assertEqual(res['code'], 2)
            self.assertEqual(res['msg'], 'no such open_id')
            self.assertEqual(res['data'], None)

    def test_post_incorrect_input8(self):
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            response = self.client.post('/api/course/comment/create',
                                        {
                                            'open_id': 1,
                                            'score': 1,
                                            'content': 'content',
                                            'isanonymous': 'true',
                                            'course_name': course_name,
                                            'course_id': course_id,
                                        })
            res = response.json()

            self.assertEqual(res['code'], 2)
            self.assertEqual(res['msg'], 'user not bound')
            self.assertEqual(res['data'], None)

    def test_post_incorrect_input9(self):
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            self.client.post('/api/welcome/account_bind',
                             {
                                 'open_id': '1',
                                 'student_id': data_for_test['username'],
                                 'password': data_for_test['password'],
                             })
            response = self.client.post('/api/course/comment/create',
                                        {
                                            'open_id': 1,
                                            'score': 1.5,
                                            'content': 'content',
                                            'isanonymous': 'true',
                                            'course_name': course_name,
                                            'course_id': course_id,
                                        })
            res = response.json()

            self.assertEqual(res['code'], 1)
            self.assertEqual(res['msg'], 'The given score should be int')
            self.assertEqual(res['data'], None)

    def test_post_incorrect_input10(self):
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            self.client.post('/api/welcome/account_bind',
                             {
                                 'open_id': '1',
                                 'student_id': data_for_test['username'],
                                 'password': data_for_test['password'],
                             })
            response = self.client.post('/api/course/comment/create',
                                        {
                                            'open_id': 1,
                                            'score': 6,
                                            'content': 'content',
                                            'isanonymous': 'true',
                                            'course_name': course_name,
                                            'course_id': course_id,
                                        })
            res = response.json()

            self.assertEqual(res['code'], 1)
            self.assertEqual(res['msg'], 'The given score is out of range')
            self.assertEqual(res['data'], None)


class CommentListViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_get_correct_input1(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password'],
                         })
        user = User.get_by_openid(1)
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            result = []
            id = 50
            for i in range(0, 100):
                create_time = current_stamp()
                comment = Comment.objects.create(isanonymous=0, course_id=course_id, course_name=course_name,
                                                 comment_time=create_time, commenter_id=user.id,
                                                 content='content' + str(i), score=i % 5 + 1)
                if i == 50:
                    id = comment.id

            response = self.client.get('/api/course/comment/list',
                                       {
                                           'open_id': 1,
                                       })
            res = response.json()
            all_comments = [{
                                'time': float(x.comment_time),
                                'content': x.content,
                                'id': x.id,
                                'real_name': x.get_commenter_name(),
                                'course_name': x.course_name,
                                'course_id': x.course_id,
                            }
                            for x in Comment.objects.all()]
            result = sorted(all_comments, key=lambda d: d['time'], reverse=True)
            length = len(result)
            if length > 10:
                result = result[0:10]
            self.assertEqual(res['code'], 0)
            self.assertEqual(res['msg'], '')
            self.assertEqual(res['data'], result)

    def test_get_correct_input2(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password'],
                         })
        user = User.get_by_openid(1)
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            result = []
            id = 50
            for i in range(0, 100):
                create_time = current_stamp()
                comment = Comment.objects.create(isanonymous=0, course_id=course_id, course_name=course_name,
                                       comment_time=create_time, commenter_id=user.id,
                                       content='content' + str(i), score=i % 5 + 1)
                if i == 50:
                    id = comment.id

            response = self.client.get('/api/course/comment/list',
                                       {
                                           'open_id': 1,
                                           'end_id': id,
                                       })
            res = response.json()
            all_comments = [{
                                'time': float(x.comment_time),
                                'content': x.content,
                                'id': x.id,
                                'real_name': x.get_commenter_name(),
                                'course_name': x.course_name,
                                'course_id': x.course_id,
                            }
                            for x in Comment.objects.all()]
            end_time = float(Comment.objects.get(id=id).comment_time)
            comments = []
            for cmt in all_comments:
                if cmt['time'] < end_time:
                    comments.append(cmt)
            result = sorted(comments, key=lambda d: d['time'], reverse=True)
            length = len(result)
            if length > 10:
                result = result[0:10]
            self.assertEqual(res['code'], 0)
            self.assertEqual(res['msg'], '')
            self.assertEqual(res['data'], result)

    def test_get_correct_input3(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password'],
                         })
        user = User.get_by_openid(1)
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            result = []
            id = 50
            for i in range(0, 100):
                create_time = current_stamp()
                comment = Comment.objects.create(isanonymous=0, course_id=course_id, course_name=course_name,
                                                 comment_time=create_time, commenter_id=user.id,
                                                 content='content' + str(i), score=i % 5 + 1)
                if i == 50:
                    id = comment.id

            response = self.client.get('/api/course/comment/list',
                                       {
                                           'open_id': 1,
                                           'course_id': course_id,
                                       })
            res = response.json()
            all_comments = [{
                                'time': float(x.comment_time),
                                'content': x.content,
                                'id': x.id,
                                'real_name': x.get_commenter_name(),
                                'course_name': x.course_name,
                                'course_id': x.course_id,
                            }
                            for x in Comment.objects.all()]
            comments = []
            for cmt in all_comments:
                if cmt['course_id'] == course_id:
                    comments.append(cmt)
            result = sorted(comments, key=lambda d: d['time'], reverse=True)
            length = len(result)
            if length > 10:
                result = result[0:10]
            self.assertEqual(res['code'], 0)
            self.assertEqual(res['msg'], '')
            self.assertEqual(res['data'], result)

    def test_get_correct_input4(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password'],
                         })
        user = User.get_by_openid(1)
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            result = []
            id = 50
            for i in range(0, 100):
                create_time = current_stamp()
                comment = Comment.objects.create(isanonymous=0, course_id=course_id, course_name=course_name,
                                                 comment_time=create_time, commenter_id=user.id,
                                                 content='content' + str(i), score=i % 5 + 1)
                if i == 50:
                    id = comment.id

            response = self.client.get('/api/course/comment/list',
                                       {
                                           'open_id': 1,
                                           'end_id': id,
                                           'course_id': course_id,
                                       })
            res = response.json()
            all_comments = [{
                                'time': float(x.comment_time),
                                'content': x.content,
                                'id': x.id,
                                'real_name': x.get_commenter_name(),
                                'course_name': x.course_name,
                                'course_id': x.course_id,
                            }
                            for x in Comment.objects.all()]
            end_time = float(Comment.objects.get(id=id).comment_time)
            comments = []
            for cmt in all_comments:
                if cmt['time'] < end_time and cmt['course_id'] == course_id:
                    comments.append(cmt)
            result = sorted(comments, key=lambda d: d['time'], reverse=True)
            length = len(result)
            if length > 10:
                result = result[0:10]
            self.assertEqual(res['code'], 0)
            self.assertEqual(res['msg'], '')
            self.assertEqual(res['data'], result)

    def test_get_incorrect_input1(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password'],
                         })
        user = User.get_by_openid(1)
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            result = []
            id = 50
            for i in range(0, 100):
                create_time = current_stamp()
                comment = Comment.objects.create(isanonymous=0, course_id=course_id, course_name=course_name,
                                                 comment_time=create_time, commenter_id=user.id,
                                                 content='content' + str(i), score=i % 5 + 1)
                if i == 50:
                    id = comment.id

            response = self.client.get('/api/course/comment/list',
                                       {
                                           'end_id': id,
                                           'course_id': course_id,
                                       })
            res = response.json()
            self.assertEqual(res['code'], 1)
            self.assertEqual(res['msg'], 'Field "open_id" required')
            self.assertEqual(res['data'], None)

    def test_get_incorrect_input2(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password'],
                         })
        user = User.get_by_openid(1)
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            result = []
            id = 50
            for i in range(0, 100):
                create_time = current_stamp()
                comment = Comment.objects.create(isanonymous=0, course_id=course_id, course_name=course_name,
                                                 comment_time=create_time, commenter_id=user.id,
                                                 content='content' + str(i), score=i % 5 + 1)
                if i == 50:
                    id = comment.id

            response = self.client.get('/api/course/comment/list',
                                       {
                                           'open_id': 2,
                                           'end_id': id,
                                           'course_id': course_id,
                                       })
            res = response.json()
            self.assertEqual(res['code'], 2)
            self.assertEqual(res['msg'], 'no such open_id')
            self.assertEqual(res['data'], None)

    def test_get_incorrect_input3(self):
        user = User.get_by_openid(1)
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            result = []
            id = 50
            for i in range(0, 100):
                create_time = current_stamp()
                comment = Comment.objects.create(isanonymous=0, course_id=course_id, course_name=course_name,
                                                 comment_time=create_time, commenter_id=user.id,
                                                 content='content' + str(i), score=i % 5 + 1)
                if i == 50:
                    id = comment.id

            response = self.client.get('/api/course/comment/list',
                                       {
                                           'open_id': 1,
                                           'end_id': id,
                                           'course_id': course_id,
                                       })
            res = response.json()
            self.assertEqual(res['code'], 2)
            self.assertEqual(res['msg'], 'user not bound')
            self.assertEqual(res['data'], None)

    def test_get_incorrect_input4(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password'],
                         })
        user = User.get_by_openid(1)
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            result = []
            id = 50
            for i in range(0, 100):
                create_time = current_stamp()
                comment = Comment.objects.create(isanonymous=0, course_id=course_id, course_name=course_name,
                                                 comment_time=create_time, commenter_id=user.id,
                                                 content='content' + str(i), score=i % 5 + 1)
                if i == 50:
                    id = comment.id

            response = self.client.get('/api/course/comment/list',
                                       {
                                           'open_id': 1,
                                           'end_id': 50.1,
                                           'course_id': course_id,
                                       })
            res = response.json()
            self.assertEqual(res['code'], 1)
            self.assertEqual(res['msg'], 'The given id should be int')
            self.assertEqual(res['data'], None)

    def test_get_incorrect_input5(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password'],
                         })
        user = User.get_by_openid(1)
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            result = []
            id = 50
            for i in range(0, 100):
                create_time = current_stamp()
                comment = Comment.objects.create(isanonymous=0, course_id=course_id, course_name=course_name,
                                                 comment_time=create_time, commenter_id=user.id,
                                                 content='content' + str(i), score=i % 5 + 1)
                if i == 50:
                    id = comment.id

            response = self.client.get('/api/course/comment/list',
                                       {
                                           'open_id': 1,
                                           'end_id': 10000,
                                           'course_id': course_id,
                                       })
            res = response.json()
            self.assertEqual(res['code'], 2)
            self.assertEqual(res['msg'], 'no such id')
            self.assertEqual(res['data'], None)

    def test_get_incorrect_input6(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password'],
                         })
        user = User.get_by_openid(1)
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            result = []
            id = 50
            for i in range(0, 100):
                create_time = current_stamp()
                comment = Comment.objects.create(isanonymous=0, course_id=course_id, course_name=course_name,
                                                 comment_time=create_time, commenter_id=user.id,
                                                 content='content' + str(i), score=i % 5 + 1)
                if i == 50:
                    id = comment.id

            response = self.client.get('/api/course/comment/list',
                                       {
                                           'open_id': 1,
                                           'end_id': 50.1,
                                       })
            res = response.json()
            self.assertEqual(res['code'], 1)
            self.assertEqual(res['msg'], 'The given id should be int')
            self.assertEqual(res['data'], None)

    def test_get_incorrect_input7(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password'],
                         })
        user = User.get_by_openid(1)
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        params = {
            'apikey': 'camustest',
            'apisecret': 'camustest',
        }
        response = requests.post(url, json=params)
        r = json.loads(response.content.decode())['classes']
        if len(r) > 0:
            course_id = r[0]['courseid']
            course_name = r[0]['coursename']
            result = []
            id = 50
            for i in range(0, 100):
                create_time = current_stamp()
                comment = Comment.objects.create(isanonymous=0, course_id=course_id, course_name=course_name,
                                       comment_time=create_time, commenter_id=user.id,
                                       content='content' + str(i), score=i % 5 + 1)
                if i == 50:
                    id = comment.id

            response = self.client.get('/api/course/comment/list',
                                       {
                                           'open_id': 1,
                                           'end_id': 10000,
                                       })
            res = response.json()
            self.assertEqual(res['code'], 2)
            self.assertEqual(res['msg'], 'no such id')
            self.assertEqual(res['data'], None)


class EventDetailViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_get_correct_input(self):
        event = self.createEventForTest()

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '0',
                                   })
        res = response.json()

        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], event)

    def test_get_incorrect_input1(self):
        event = self.createEventForTest()

        response = self.client.get('/api/event/detail',
                                   {
                                       'id': '0',
                                   })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "open_id" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input2(self):
        event = self.createEventForTest()

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                   })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "id" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input3(self):
        event = self.createEventForTest()

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 2,
                                       'id': '1',
                                   })
        res = response.json()

        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'no such open_id')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input4(self):
        event = self.createEventForTest()

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '5',
                                   })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given id is out of range')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input5(self):
        event = self.createEventForTest()

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '5.6',
                                   })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given id should be int')
        self.assertEqual(res['data'], None)

    def test_post_correct_input(self):
        self.createEventForTest()
        new_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.post('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'name': 'new_name',
                                       'date': new_date,
                                       'content': 'new_content',
                                       'id': '0',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], {'id': 0})

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '0',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], {
                                       'name': 'new_name',
                                       'date': new_date,
                                       'content': 'new_content',
        })

    def test_post_incorrect_input1(self):
        event = self.createEventForTest()
        new_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.post('/api/event/detail',
                                   {
                                       'name': 'new_name',
                                       'date': new_date,
                                       'content': 'new_content',
                                       'id': '0',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "open_id" required')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '0',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], event)

    def test_post_incorrect_input2(self):
        event = self.createEventForTest()
        new_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.post('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'date': new_date,
                                       'content': 'new_content',
                                       'id': '0',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "name" required')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '0',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], event)

    def test_post_incorrect_input3(self):
        event = self.createEventForTest()
        new_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.post('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'name': 'new_name',
                                       'content': 'new_content',
                                       'id': '0',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "date" required')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '0',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], event)

    def test_post_incorrect_input4(self):
        event = self.createEventForTest()
        new_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.post('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'name': 'new_name',
                                       'date': new_date,
                                       'id': '0',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "content" required')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '0',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], event)

    def test_post_incorrect_input5(self):
        event = self.createEventForTest()
        new_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.post('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'name': 'new_name',
                                       'date': new_date,
                                       'content': 'new_content',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "id" required')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '0',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], event)

    def test_post_incorrect_input6(self):
        event = self.createEventForTest()
        new_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.post('/api/event/detail',
                                   {
                                       'open_id': 2,
                                       'name': 'new_name',
                                       'date': new_date,
                                       'content': 'new_content',
                                       'id': '0',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'no such open_id')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '0',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], event)

    def test_post_incorrect_input7(self):
        event = self.createEventForTest()
        new_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.post('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'name': 'new_name',
                                       'date': new_date,
                                       'content': 'new_content',
                                       'id': '1.5',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given id should be int')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '0',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], event)

    def test_post_incorrect_input8(self):
        event = self.createEventForTest()
        new_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.post('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'name': 'new_name',
                                       'date': new_date,
                                       'content': 'new_content',
                                       'id': '-1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given id is out of range')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '0',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], event)

    def test_post_incorrect_input9(self):
        event = self.createEventForTest()
        response = self.client.post('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'name': 'new_name',
                                       'date': 'incorrect date',
                                       'content': 'new_content',
                                       'id': '0',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'incorrect given date')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '0',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], event)

    def createEventForTest(self):
        self.client.post('/api/event/create',
                         {
                             'open_id': 1,
                             'name': 'name',
                             'date': datetime.date.today().strftime('%Y-%m-%d'),
                             'content': 'content',
                         })
        return {
            'name': 'name',
            'content': 'content',
            'date': datetime.date.today().strftime('%Y-%m-%d'),
        }


class EventListViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_get_correct_input1(self):
        events = self.createEventForTest(100)
        response = self.client.get('/api/event/list',
                                   {
                                       'open_id': 1,
                                       'mode': 'day',
                                   })
        res = response.json()

        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], {'events': events[0:10]})

    def test_get_correct_input2(self):
        result = self.createEventForTest(100)
        events = []
        for x in result:
            for y in x:
                if datetime.datetime.strptime(y['date'], '%Y-%m-%d').month == datetime.date.today().month:
                    y.pop('content')
                    events.append(y)
        response = self.client.get('/api/event/list',
                                   {
                                       'open_id': 1,
                                       'mode': 'month',
                                       'month': month_now_str(),
                                   })
        res = response.json()

        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], events)

    def test_get_incorrect_input1(self):
        result = self.createEventForTest(100)
        events = []
        for x in result:
            if datetime.datetime.strptime(x[0]['date'], '%Y-%m-%d').month == datetime.date.today().month:
                events.append(x)
        response = self.client.get('/api/event/list',
                                   {
                                       'mode': 'month',
                                       'month': month_now_str(),
                                   })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "open_id" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input2(self):
        result = self.createEventForTest(100)
        events = []
        for x in result:
            if datetime.datetime.strptime(x[0]['date'], '%Y-%m-%d').month == datetime.date.today().month:
                events.append(x)
        response = self.client.get('/api/event/list',
                                   {
                                       'open_id': 1,
                                       'month': month_now_str(),
                                   })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "mode" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input3(self):
        result = self.createEventForTest(100)
        events = []
        for x in result:
            if datetime.datetime.strptime(x[0]['date'], '%Y-%m-%d').month == datetime.date.today().month:
                events.append(x)
        response = self.client.get('/api/event/list',
                                   {
                                       'open_id': 1,
                                       'mode': 'month',
                                   })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "month" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input4(self):
        result = self.createEventForTest(100)
        events = []
        for x in result:
            if datetime.datetime.strptime(x[0]['date'], '%Y-%m-%d').month == datetime.date.today().month:
                events.append(x)
        response = self.client.get('/api/event/list',
                                   {
                                       'open_id': 2,
                                       'mode': 'month',
                                       'month': month_now_str(),
                                   })
        res = response.json()

        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'no such open_id')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input5(self):
        result = self.createEventForTest(100)
        events = []
        for x in result:
            if datetime.datetime.strptime(x[0]['date'], '%Y-%m-%d').month == datetime.date.today().month:
                events.append(x)
        response = self.client.get('/api/event/list',
                                   {
                                       'open_id': 1,
                                       'mode': 'month',
                                       'month': 'incorrect month',
                                   })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'incorrect given month')
        self.assertEqual(res['data'], None)

    def createEventForTest(self, n):
        result = []
        for i in range(0, n):
            temp = self.client.post('/api/event/create',
                             {
                                 'open_id': 1,
                                 'name': 'name' + str(i),
                                 'date': (datetime.date.today() + datetime.timedelta(days=i)).strftime('%Y-%m-%d'),
                                 'content': 'content' + str(i),
                             })
            result.append([{
                'name': 'name' + str(i),
                'id': i,
                'content': 'content' + str(i),
                'date': (datetime.date.today() + datetime.timedelta(days=i)).strftime('%Y-%m-%d'),
            }])
        return result


class EventCreateViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_post_correct_input(self):
        response = self.client.post('/api/event/create',
                                    {
                                        'open_id': 1,
                                        'name': 'name',
                                        'date': datetime.date.today().strftime('%Y-%m-%d'),
                                        'content': 'content',
                                    })
        res = response.json()
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], {'id': 0})

    def test_post_incorrect_input1(self):
        response = self.client.post('/api/event/create',
                                    {
                                        'name': 'name',
                                        'date': datetime.date.today().strftime('%Y-%m-%d'),
                                        'content': 'content',
                                    })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "open_id" required')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input2(self):
        response = self.client.post('/api/event/create',
                                    {
                                        'open_id': 1,
                                        'date': datetime.date.today().strftime('%Y-%m-%d'),
                                        'content': 'content',
                                    })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "name" required')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input3(self):
        response = self.client.post('/api/event/create',
                                    {
                                        'open_id': 1,
                                        'name': 'name',
                                        'content': 'content',
                                    })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "date" required')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input4(self):
        response = self.client.post('/api/event/create',
                                    {
                                        'open_id': 1,
                                        'name': 'name',
                                        'date': datetime.date.today().strftime('%Y-%m-%d'),
                                    })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "content" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input5(self):
        response = self.client.post('/api/event/create',
                                    {
                                        'open_id': 2,
                                        'name': 'name',
                                        'date': datetime.date.today().strftime('%Y-%m-%d'),
                                        'content': 'content',
                                    })
        res = response.json()

        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'no such open_id')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input6(self):
        response = self.client.post('/api/event/create',
                                    {
                                        'open_id': 1,
                                        'name': 'name',
                                        'date': 'incorrect date',
                                        'content': 'content',
                                    })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'incorrect given date')
        self.assertEqual(res['data'], None)


class EventDeleteViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_post_correct_input(self):
        event_id = (self.client.post('/api/event/create',
                                    {
                                        'open_id': 1,
                                        'name': 'name',
                                        'date': datetime.date.today().strftime('%Y-%m-%d'),
                                        'content': 'content',
                                    })).json()['data']['id']
        response = self.client.post('/api/event/delete',
                                    {
                                        'open_id': 1,
                                        'id': event_id,
                                    })
        res = response.json()

        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input1(self):
        event_id = (self.client.post('/api/event/create',
                                     {
                                         'open_id': 1,
                                         'name': 'name',
                                         'date': datetime.date.today().strftime('%Y-%m-%d'),
                                         'content': 'content',
                                     })).json()['data']['id']
        response = self.client.post('/api/event/delete',
                                    {
                                        'id': event_id,
                                    })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "open_id" required')
        self.assertEqual(res['data'], None)


    def test_post_incorrect_input2(self):
        event_id = (self.client.post('/api/event/create',
                                    {
                                        'open_id': 1,
                                        'name': 'name',
                                        'date': datetime.date.today().strftime('%Y-%m-%d'),
                                        'content': 'content',
                                    })).json()['data']['id']
        response = self.client.post('/api/event/delete',
                                    {
                                        'open_id': 1,
                                    })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "id" required')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input3(self):
        event_id = (self.client.post('/api/event/create',
                                    {
                                        'open_id': 1,
                                        'name': 'name',
                                        'date': datetime.date.today().strftime('%Y-%m-%d'),
                                        'content': 'content',
                                    })).json()['data']['id']
        response = self.client.post('/api/event/delete',
                                    {
                                        'open_id': 2,
                                        'id': event_id,
                                    })
        res = response.json()

        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'no such open_id')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input4(self):
        event_id = (self.client.post('/api/event/create',
                                    {
                                        'open_id': 1,
                                        'name': 'name',
                                        'date': datetime.date.today().strftime('%Y-%m-%d'),
                                        'content': 'content',
                                    })).json()['data']['id']
        response = self.client.post('/api/event/delete',
                                    {
                                        'open_id': 1,
                                        'id': event_id + 1,
                                    })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given id is out of range')
        self.assertEqual(res['data'], None)


class ReadNoticeRecordViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_post_correct_input(self):
        response = self.client.post('/api/read/notice/record',
                                    {
                                        'open_id': 1,
                                        'type': 1,
                                        'name': 'name',
                                        'course_id': 'course_id',
                                    })
        res = response.json()

        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input1(self):
        response = self.client.post('/api/read/notice/record',
                                    {
                                        'type': 1,
                                        'name': 'name',
                                        'course_id': 'course_id',
                                    })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "open_id" required')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input2(self):
        response = self.client.post('/api/read/notice/record',
                                    {
                                        'open_id': 1,
                                        'name': 'name',
                                        'course_id': 'course_id',
                                    })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "type" required')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input3(self):
        response = self.client.post('/api/read/notice/record',
                                    {
                                        'open_id': 1,
                                        'type': 1,
                                        'course_id': 'course_id',
                                    })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "name" required')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input4(self):
        response = self.client.post('/api/read/notice/record',
                                    {
                                        'open_id': 1,
                                        'type': 1,
                                        'name': 'name',
                                    })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "course_id" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input5(self):
        response = self.client.post('/api/read/notice/record',
                                    {
                                        'open_id': 2,
                                        'type': 1,
                                        'name': 'name',
                                        'course_id': 'course_id',
                                    })
        res = response.json()

        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'no such open_id')
        self.assertEqual(res['data'], None)