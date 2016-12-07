from wechat.wrapper import WeChatView, WeChatLib
from wechat.handlers import *
from wechat.models import *
from XuetangPlus.settings import WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET
from XuetangPlus.settings import get_redirect_url

class CustomWeChatView(WeChatView):

    lib = WeChatLib(WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET)

    handlers = [
        HelpOrSubscribeHandler, UnbindOrUnsubscribeHandler, AccountBindHandler, ViewPersonalInformationHandler,
        CourseSearchHandler, MyCourseHandler, CommunicateHandler, NotificationHandler, LibraryRemainsHandler,
        MyCalendarHandler, SchoolCalendarHandler, NavigationHandler
    ]

    error_message_handler = ErrorHandler
    default_handler = DefaultHandler

    event_keys = {
        'help': 'WELCOME_HELP',
        'account_bind': 'WELCOME_BIND',
        'course_search': 'LEARN_SEARCH',
        'my_course': 'LEARN_COURSE',
        'communicate': 'LEARN_COMMUNICATE',
        'notification': 'LEARN_NOTIFICATION',
        'library_remains': 'LIFE_LIBRARY',
        'my_calendar': 'LIFE_MY_CALENDAR',
        'school_calendar': 'LIFE_SCHOOL_CALENDAR',
        'navigation': 'LIFE_NAVIGATION',
    }

    # define url
    event_urls = {
        'help': 'welcome/help',
        'account_bind': 'welcome/account_bind',
        'search_course': 'learn/search_course',
        'course_list': 'learn/course_list',
        'communication': 'learn/communication',
        'notice_panel': 'learn/notice_panel',
        'calendar': 'life/calendar',
    }

    menu = {
        'button': [
            {
                'name': '欢迎',
                'sub_button': [
                    {
                        'type': 'click',
                        'name': '帮助',
                        'key': event_keys['help'],
                    },
                    {
                        'type': 'click',
                        'name': '绑定账号',
                        'key': event_keys['account_bind'],
                    }
                ]
            },
            {
                'name': '爱学习',
                'sub_button': [
                    {
                        'type': 'click',
                        'name': '课程搜索',
                        'key': event_keys['course_search'],
                    },
                    {
                        'type': 'click',
                        'name': '本人课程',
                        'key': event_keys['my_course'],
                    },
                    {
                        'type': 'click',
                        'name': '师生交流',
                        'key': event_keys['communicate'],
                    },
                    {
                        'type': 'click',
                        'name': '公告及作业',
                        'key': event_keys['notification'],
                    },
                ]
            },
            {
                'name': '乐生活',
                'sub_button': [
                    {
                        'type': 'click',
                        'name': '文图查座',
                        'key': event_keys['library_remains'],
                    },
                    {
                        'type': 'click',
                        'name': '个人日历',
                        'key': event_keys['my_calendar'],
                    },
                    {
                        'type': 'click',
                        'name': '校历查询',
                        'key': event_keys['school_calendar'],
                    },
                    {
                        'type': 'location_select',
                        'name': '校园导航',
                        'key': event_keys['navigation']
                    },

                ]
            }
        ]
    }

    @classmethod
    def update_menu(cls):
        return cls.lib.set_wechat_menu(cls.menu)

