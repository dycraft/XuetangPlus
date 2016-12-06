# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
import requests
import json

__author__ = "Epsirom"


class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，没有找到您需要的信息:(')


class HelpOrSubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe') or \
               self.is_event_click(self.view.event_keys['help'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
        })


class UnbindOrUnsubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        if self.user.username == '':
            return  self.reply_text("您还未绑定")
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
            return self.reply_text("请您重新进行绑定，若仍然失败请联系管理员。")


class BindAccountHandler(WeChatHandler):

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
            return  self.reply_text("请先进行绑定")
        dic = { 'undergraduate': '本科就读',
                'master': '硕士',
                'doctor': '博士',
                'teacher': '教师'}
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
            return  self.reply_text("请先进行绑定")
        return self.reply_single_news({
            'Title': '欢迎使用课程搜索',
            'Description': '在这里你可以方便的查询课程的信息',
            'Url': self.url_course_search(),
        })


class MyCourseHandler(WeChatHandler):

    def check(self):
        return self.is_text('我的课程')

    def handle(self):
        if self.user.username == '':
            return  self.reply_text("请先进行绑定")
        response = requests.post('http://se.zhuangty.com:8000/curriculum/' + self.user.username)
        description = '暂时无法获得，接口尚未完善'
        dic = {
            1: '8:00',
            2: '9:50',
            3: '13:30',
            4: '15:20',
            5: '17:05',
            6: '19:20',
        }
        if response.status_code == 200:
            res = json.loads(response.content.decode())
            for course in res['classes']:
                description = description + '\n课程代号：' + course['coursid']
                description = description + '\n课程名称：' + course['coursename']
                description = description + '\n课程星期：' + course['time'][0]
                description = description + '\n课程时间：' + dic[course['time'][1]]
                description = description + '\n课程教师：' + course['teacher']
                description = description + '\n课程教室：' + course['classroom']
                description = description + '\n课程周数：' + course['week'] + '\n'
        else:
            description = '请您重新进行绑定，若仍然失败请联系管理员。'
        return self.reply_single_news({
            'Title': '欢迎查看您的课程',
            'Description': description,
            'Url': self.url_my_course(),
        })


class CommunicateHandler(WeChatHandler):

    def check(self):
        return self.is_text('师生交流')

    def handle(self):
        if self.user.username == '':
            return  self.reply_text("请先进行绑定")
        return self.reply_single_news({
            'Title': '欢迎使用师生交流',
            'Description': '有一门课程有新消息，点击查看。',
            'Url': self.url_communicate(),
        })


class NotificationHandler(WeChatHandler):

    def check(self):
        return self.is_text('通知面板')

    def handle(self):
        if self.user.username == '':
            return  self.reply_text("请先进行绑定")
        response = requests.post('http://se.zhuangty.com:8000/curriculum/' + self.user.username)
        if response.status_code == 200:
            description = '公告：'
            res = json.loads(response.content.decode())
            dic = { 'read': '已读',
                    'unread': '未读',
                    'true': '已批改',
                    'false': '未批改'}
            for course in res['classes']:
                response_inform = requests.post('http://se.zhuangty.com:8000/learnhelper/'
                                                + self.user.username + '/courses/' + course['coursid']
                                                + '/notices')
                if response_inform.status_code == 200:
                    resp = json.loads(response_inform.content.decode())
                    description = description + '\n标题：' + resp['title']
                    description = description + '\n发布时间：' + resp['publishtime']
                    description = description + '\n状态：' + dic[resp['state']]
                    description = description + '\n内容：' + resp['content'] + '\n\n'
                else:
                    return self.reply_single_news({
                        'Title': '欢迎使用通知面板',
                        'Description': '请您重新进行绑定，若仍然失败请联系管理员。',
                        'Url': self.url_notification(),
                    })

            description += '\n作业：'
            for course in res['classes']:
                response_work = requests.post('http://se.zhuangty.com:8000/learnhelper/'
                                                + self.user.username + '/courses/' + course['coursid']
                                                + '/assignments')
                if response_work.status_code == 200:
                    resp = json.loads(response_work.content.decode())
                    description = description + '\n标题：' + resp['title']
                    description = description + '\n作业内容：' + resp['detail']
                    description = description + '\n发布时间：' + resp['startdate']
                    description = description + '\n截止时间：' + resp['duedate']
                    description = description + '\n批改状态：' + dic[resp['scored']]
                    description = description + '\n批改老师：' + resp['evaluatingteacher']
                    description = description + '\n批改时间：' + resp['evaluatingdate']
                    description = description + '\n批注：' + resp['comment']
                    description = description + '\n作业分数：' + resp['grade'] + '\n\n'
                else:
                    return self.reply_single_news({
                        'Title': '欢迎使用通知面板',
                        'Description': '请您重新进行绑定，若仍然失败请联系管理员。',
                        'Url': self.url_notification(),
                    })
        else:
            return self.reply_single_news({
                'Title': '欢迎使用通知面板',
                'Description': '请您重新进行绑定，若仍然失败请联系管理员。',
                'Url': self.url_notification(),
            })


        return self.reply_single_news({
            'Title': '欢迎使用通知面板',
            'Description': description,
            'Url': self.url_notification(),
        })


class MyCalendarHandler(WeChatHandler):

    def check(self):
        return self.is_text('我的日历')

    def handle(self):
        if self.user.username == '':
            return  self.reply_text("请先进行绑定")
        return self.reply_single_news({
            'Title': '欢迎使用个人日历',
            'Description': '在这里你可以方便查看和管理你的日程',
            'Url': self.url_my_calendar(),
        })


class SchoolCalendarHandler(WeChatHandler):

    def check(self):
        return self.is_text('校园日历')

    def handle(self):
        if self.user.username == '':
            return  self.reply_text("请先进行绑定")
        return self.reply_single_news({
            'Title': '欢迎使用校园日历',
            'Description': '方便查看校园日历',
            'Url': self.url_school_calendar(),
        })


class NavigationHandler(WeChatHandler):

    def check(self):
        return self.is_text('地图')

    def handle(self):
        if self.user.username == '':
            return  self.reply_text("请先进行绑定")
        return self.reply_single_news({
            'Title': '欢迎使用地图',
            'Description': '方便查看地图',
            'Url': self.url_navigation(),
        })