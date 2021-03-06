# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
from wechat.models import User, WechatConfirmation
from wechat.message_models import *
from codex.baseerror import *
from util.time import *
import requests
import json
from XuetangPlus.settings import event_keys


class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self, inputStr):
        return self.reply_text('对不起，没有找到您需要的信息:(\n您查找的内容为(' + inputStr
                               + ')\n\n我们目前支持的功能包括帮助、解绑、绑定、我的信息、查找课程、我的课程、'
                                 '课程交流、通知面板、文图、我的日历、校历、导航、提醒')


class HelpOrSubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe')

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
            'PicUrl': self.url_pic('/img/theme/help.png')
        })


class UnbindOrUnsubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        if self.user.username == '':
            return self.reply_text('您还未绑定')
        response = requests.post('http://se.zhuangty.com:8000/users/' + self.user.username + '/cancel')
        if response.status_code == 200:
            self.user.username = ''
            self.user.student_id = ''
            self.user.department = ''
            self.user.position = ''
            self.user.email = ''
            self.user.realname = ''
            self.user.save()
            return self.reply_text(self.get_message('account_unbind'))
        else:
            return self.reply_text('请您重新进行绑定，若仍然失败请联系管理员。')


class AccountBindHandler(WeChatHandler):

    def check(self):
        return self.is_text('绑定')

    def handle(self):
        if self.user.username == '':
            return self.reply_text(self.get_message('account_bind'))
        else:
            return self.reply_text('您已经绑定学号' + self.user.student_id)


class ViewPersonalInformationHandler(WeChatHandler):

    def check(self):
        return self.is_text('我的信息')

    def handle(self):
        if self.user.username == '':
            return self.reply_text('请先进行绑定')
        dic = {
            'undergraduate': '本科就读',
            'master': '硕士',
            'doctor': '博士',
            'teacher': '教师'
        }
        return self.reply_text('姓名：' + self.user.realname + '\n'
            + '学号：' + self.user.student_id + '\n'
            + '学位：' + dic[self.user.position] + '\n'
            + '院系：' + self.user.department + '\n'
            + '邮箱：' + self.user.email + '\n')


class CourseSearchHandler(WeChatHandler):

    def check(self):
        return self.is_text('查找课程')

    def handle(self):
        if self.user.username == '':
            return self.reply_text('请先进行绑定')
        return self.reply_single_news({
            'Title': '欢迎使用课程搜索',
            'Description': '在这里你可以方便的查询课程的信息',
            'Url': self.url_course_search(),
            'PicUrl': self.url_pic('/img/theme/search_course.png')
        })


class CourseListHandler(WeChatHandler):

    def check(self):
        return self.is_text('我的课程')

    def handle(self):
        if self.user.username == '':
            return self.reply_text('请先进行绑定')

        return self.reply_single_news({
            'Title': '欢迎查看您的课程',
            'Description': '点击查看课程列表',
            'Url': self.url_my_course(),
            'PicUrl': self.url_pic('/img/theme/my_course.png')
        })


class CommunicateHandler(WeChatHandler):

    def check(self):
        return self.is_text('课程交流')

    def handle(self):
        if self.user.username == '':
            return self.reply_text('请先进行绑定')

        return self.reply_single_news({
            'Title': '欢迎使用课程交流',
            'Description': '在交流中学习',
            'Url': self.url_communication(),
            'PicUrl': self.url_pic('/img/theme/communication.png')
        })


class NoticePanelHandler(WeChatHandler):

    def check(self):
        return self.is_text('通知面板')

    def handle(self):
        if self.user.username == '':
            return self.reply_text('请先进行绑定')
        return self.reply_single_news({
            'Title': '欢迎使用通知面板',
            'Description': '查看各个课程的公告与作业',
            'Url': self.url_notification(),
            'PicUrl': self.url_pic('/img/theme/notification.png')
        })


class LibraryRemainsHandler(WeChatHandler):
    def check(self):
        return self.is_text('文图') or self.is_event_click(event_keys['library_remains'])

    def handle(self):
        response = requests.post('http://se.zhuangty.com:8000/library/hs')
        if response.status_code == 200:
            res = json.loads(response.content.decode())
            reply = '文图剩余座位\n'
            reply += '\n'.join([area['name'] + '：' + str(area['left'])
                                + '/' + str(area['left'] + area['used']) for area in res['areas']])
            return self.reply_text(reply)

        else:
            return self.reply_text('很抱歉，现在无法查询到剩余座位，请稍后再试。')


class MyCalendarHandler(WeChatHandler):

    def check(self):
        return self.is_text('我的日历')

    def handle(self):
        if self.user.username == '':
            return self.reply_text('请先进行绑定')
        return self.reply_single_news({
            'Title': '欢迎使用个人日历',
            'Description': '在这里你可以方便查看和管理你的日程',
            'Url': self.url_my_calendar(),
            'PicUrl': self.url_pic('/img/theme/calendar.png')
        })


class SchoolCalendarHandler(WeChatHandler):

    def check(self):
        return self.is_text('校历') or self.is_event_click(event_keys['school_calendar'])

    def handle(self):
        response = requests.post('http://se.zhuangty.com:8000/events')
        if response.status_code == 200:
            res = json.loads(response.content.decode())
            reply = '\n'.join(['距 ' + event['name'] + (' 开始' if event['status'] == 'begin' else ' 结束')
                       + '还有' + str(event['remainingdays']) + '天' for event in res['events']])
            return self.reply_text(reply)

        else:
            return self.reply_text('很抱歉，现在无法查询到校历资讯，请稍后再试。')


class NavigationHandler(WeChatHandler):

    def check(self):
        return self.is_text('导航') or self.is_event_click(event_keys['navigation'])

    def handle(self):
        return self.reply_single_news({
            'Title': '欢迎使用校园导航',
            'Description': '输入地点进行导航',
            'Url': self.url_navigation(),
            'PicUrl': self.url_pic('/img/theme/navigation.png')
        })


class RemindHandler(WeChatHandler):

    def check(self):
        return self.is_text('提醒')

    def handle(self):
        confirm = WechatConfirmation.get_or_create()
        if self.user.student_id == '':
            return self.reply_text('请先进行绑定')
        try:
            user = User.get_by_openid(self.user.open_id)
        except:
            raise LogicError('no such open_id')

        hw_num = 0
        info_num = 0

        url = 'http://se.zhuangty.com:8000/curriculum/'
        params = {
            user.student_id
        }

        response = requests.post('http://se.zhuangty.com:8000/learnhelper/' + user.student_id + '/courses')

        if response.status_code == 200:
            res = json.loads(response.content.decode())
            for course in res['courses']:
                info_num += course['unreadnotice']
                hw_num += course['unsubmittedoperations']
        else:
            raise LogicError('Response Error')

        message_model = MessageModel()

        timenow = stamp_to_localstr_minute(current_stamp())
        model = message_model.create_remind_model(self.user.open_id, hw_num, info_num, timenow)

        model_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=';
        model_url += confirm.get_access_token()
        res = requests.post(model_url, data=json.dumps(model))

        return self.reply_text('欢迎使用提醒功能')
