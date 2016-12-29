import json
from XuetangPlus.settings import event_urls, get_redirect_url
import requests
from django.test import TestCase
import datetime
from wechat.views import CustomWeChatView
from wechat.handlers import ErrorHandler, DefaultHandler, HelpOrSubscribeHandler, UnbindOrUnsubscribeHandler, \
    AccountBindHandler, ViewPersonalInformationHandler, CourseSearchHandler, CourseListHandler, CommunicateHandler, \
    NoticePanelHandler, LibraryRemainsHandler, MyCalendarHandler, SchoolCalendarHandler, NavigationHandler
from wechat.models import User, Event

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
        self.assertEqual(inst.handle(inputStr), inst.reply_text('对不起，没有找到您需要的信息:(\n您查找的内容为(' + inputStr + ")\n我们目前支持的功能包括帮助、解绑、绑定、我的信息、查找课程、"
                                                                          "我的课程、师生交流、通知面板、文图、我的日历、"
                                                                         "校历、地图、提醒"))


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
        self.msg['Content'] = '师生交流'
        user = User.get_by_openid('1')
        inst = CommunicateHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text('请先进行绑定'))

    def test_when_correct_text2(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '师生交流'
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
            'Title': '欢迎使用师生交流',
            'Description': '有一门课程有新消息，点击查看。',
            'Url': inst.url_communicate_student(),
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

    '''诚哥注释了NavigationHandler的绑定判定'''
    '''
    def test_when_correct_text1(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '地图'
        user = User.get_by_openid('1')
        inst = NavigationHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text('请先进行绑定'))
    '''
    def test_when_correct_text2(self):
        self.msg['MsgType'] = 'text'
        self.msg['Content'] = '地图'
        '''
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        '''
        user = User.get_by_openid('1')
        inst = NavigationHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_single_news({
            'Title': '欢迎使用地图',
            'Description': '方便查看地图',
            'Url': inst.url_navigation(),
        }))

    '''
    def test_when_correct_event_click1(self):
        self.msg['MsgType'] = 'event'
        self.msg['Event'] = 'CLICK'
        self.msg['EventKey'] = 'LIFE_NAVIGATION'
        user = User.get_by_openid('1')
        inst = NavigationHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_text('请先进行绑定'))
    '''

    def test_when_correct_event_click(self):
        self.msg['MsgType'] = 'event'
        self.msg['Event'] = 'CLICK'
        self.msg['EventKey'] = 'LIFE_NAVIGATION'
        '''
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        '''
        user = User.get_by_openid('1')
        inst = NavigationHandler(CustomWeChatView, self.msg, user)
        self.assertEqual(inst.check(), True)
        self.assertEqual(inst.handle(), inst.reply_single_news({
            'Title': '欢迎使用地图',
            'Description': '方便查看地图',
            'Url': inst.url_navigation(),
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
        response = self.client.get('/api/welcome/account_bind', {})
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
        self.assertEqual(res['msg'], 'has not bind')
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
        self.assertEqual(res['msg'], 'has not bind')
        self.assertEqual(res['data'], None)

'''诚哥更改中，暂不测试'''
'''
class GetCourseIdViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_get_correct_input(self):
        self.client.post('/api/welcome/account_bind',
                         {
                             'open_id': '1',
                             'student_id': data_for_test['username'],
                             'password': data_for_test['password']
                         })
        response = self.client.get('/api/learn/notice_panel/get_course_id', {'open_id': 1})
        res = response.json()
        url = 'http://se.zhuangty.com:8000/curriculum/' + data_for_test['username']
        response = requests.post(url)
        course_ids = []
        if response.status_code == 200:
            result = json.loads(response.content.decode())
            course_ids = list(set([c['courseid'] for c in result['classes']]))
            self.assertEqual(res['code'], 0)
            self.assertEqual(res['msg'], '')
            self.assertEqual(res['data'], course_ids)
        else:
            self.assertEqual(res['code'], 0)
            self.assertEqual(res['msg'], '')
            self.assertEqual(res['data'], [])

    def test_get_incorrect_input1(self):
        response = self.client.get('/api/learn/notice_panel/get_course_id', {'sth':'sth'})
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "open_id" required')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input2(self):
        response = self.client.get('/api/learn/notice_panel/get_course_id', {'open_id': 2})
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'no such open_id')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input3(self):
        response = self.client.get('/api/learn/notice_panel/get_course_id', {'open_id': 1})
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'has not bind')
        self.assertEqual(res['data'], None)

        '''


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
            self.assertEqual(res['msg'], 'response code 400')
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
        self.assertNotEqual(res['code'], 3)
        self.assertEqual(res['msg'], 'User not found')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input3(self):
        response = self.client.get('/api/me/info',{'open_id': 1})
        res = response.json()
        self.assertNotEqual(res['code'], 2)
        self.assertEqual(res['msg'], "local variable 'course_ids' referenced before assignment")
        self.assertEqual(res['data'], None)



class EventDetailViewTestCase(TestCase):
    fixtures = ['user.json']

    def test_get_correct_input(self):
        event = self.createEventForTest()

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '1',
                                   })
        res = response.json()

        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given id is out of range')
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input1(self):
        event = self.createEventForTest()

        response = self.client.get('/api/event/detail',
                                   {
                                       'id': '1',
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

        self.assertEqual(res['code'], -1)
        self.assertEqual(res['msg'], "invalid literal for int() with base 10: '5.6'")
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
                                       'id': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], -1)
        self.assertEqual(res['msg'], 'unorderable types: int() > str()')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given id is out of range')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input1(self):
        event = self.createEventForTest()
        new_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.post('/api/event/detail',
                                   {
                                       'name': 'new_name',
                                       'date': new_date,
                                       'content': 'new_content',
                                       'id': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "open_id" required')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given id is out of range')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input2(self):
        event = self.createEventForTest()
        new_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.post('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'date': new_date,
                                       'content': 'new_content',
                                       'id': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "name" required')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given id is out of range')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input3(self):
        event = self.createEventForTest()
        new_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.post('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'name': 'new_name',
                                       'content': 'new_content',
                                       'id': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "date" required')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given id is out of range')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input4(self):
        event = self.createEventForTest()
        new_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.post('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'name': 'new_name',
                                       'date': new_date,
                                       'id': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'Field "content" required')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given id is out of range')
        self.assertEqual(res['data'], None)

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
                                       'id': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given id is out of range')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input6(self):
        event = self.createEventForTest()
        new_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.post('/api/event/detail',
                                   {
                                       'open_id': 2,
                                       'name': 'new_name',
                                       'date': new_date,
                                       'content': 'new_content',
                                       'id': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 2)
        self.assertEqual(res['msg'], 'no such open_id')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given id is out of range')
        self.assertEqual(res['data'], None)

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
        self.assertEqual(res['code'], -1)
        self.assertEqual(res['msg'], 'unorderable types: int() > str()')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given id is out of range')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input8(self):
        event = self.createEventForTest()
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
        self.assertEqual(res['code'], -1)
        self.assertEqual(res['msg'], 'unorderable types: int() > str()')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given id is out of range')
        self.assertEqual(res['data'], None)

    def test_post_incorrect_input9(self):
        event = self.createEventForTest()
        response = self.client.post('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'name': 'new_name',
                                       'date': 'incorrect date',
                                       'content': 'new_content',
                                       'id': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], -1)
        self.assertEqual(res['msg'], 'unorderable types: int() > str()')
        self.assertEqual(res['data'], None)

        response = self.client.get('/api/event/detail',
                                   {
                                       'open_id': 1,
                                       'id': '1',
                                   })
        res = response.json()
        self.assertEqual(res['code'], 1)
        self.assertEqual(res['msg'], 'The given id is out of range')
        self.assertEqual(res['data'], None)

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

        self.assertEqual(res['code'], -1)
        self.assertEqual(res['msg'], "An error occurred in the current transaction. You can't execute queries until the end of the 'atomic' block.")
        self.assertEqual(res['data'], None)

    def test_get_correct_input2(self):
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

        self.assertEqual(res['code'], -1)
        self.assertEqual(res['msg'], "An error occurred in the current transaction. You can't execute queries until the end of the 'atomic' block.")
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input1(self):
        result = self.createEventForTest(100)
        events = []
        for x in result:
            if datetime.datetime.strptime(x[0]['date'], '%Y-%m-%d').month == datetime.date.today().month:
                events.append(x)
        response = self.client.get('/api/event/list',
                                   {
                                       'mode': 'month',
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
                                       'open_id': 2,
                                       'mode': 'month',
                                   })
        res = response.json()

        self.assertEqual(res['code'], -1)
        self.assertEqual(res['msg'], "An error occurred in the current transaction. You can't execute queries until the end of the 'atomic' block.")
        self.assertEqual(res['data'], None)

    def test_get_incorrect_input4(self):
        result = self.createEventForTest(100)
        events = []
        for x in result:
            if datetime.datetime.strptime(x[0]['date'], '%Y-%m-%d').month == datetime.date.today().month:
                events.append(x)
        response = self.client.get('/api/event/list',
                                   {
                                       'open_id': 1,
                                       'mode': 'incorrect mode',
                                   })
        res = response.json()

        self.assertEqual(res['code'], 0)
        self.assertEqual(res['msg'], '')
        self.assertEqual(res['data'], None)

    def createEventForTest(self, n):
        result = []
        for i in range(0, n):
            self.client.post('/api/event/create',
                             {
                                 'open_id': 1,
                                 'name': 'name' + str(i),
                                 'date': (datetime.date.today() + datetime.timedelta(days=i)).strftime('%Y-%m-%d'),
                                 'content': 'content' + str(i),
                             })
            result.append([{
                'name': 'name' + str(i),
                'id': i + 1,
                'content': 'content' + str(i),
                'date': (datetime.date.today() + datetime.timedelta(days=i)).strftime('%Y-%m-%d'),
            }])
        return result


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
        self.assertEqual(res['data'], {'id': 1})

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
        self.assertEqual(res['msg'], 'User not found')
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

        self.assertEqual(res['code'], -1)
        self.assertEqual(res['msg'], "time data 'incorrect date' does not match format '%Y-%m-%d'")
        self.assertEqual(res['data'], None)