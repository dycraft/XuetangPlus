from wechat.wrapper import WeChatView, WeChatLib
from wechat.handlers import *
from wechat.models import *
from XuetangPlus.settings import WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET
from XuetangPlus.settings import get_url, get_redirect_url

class CustomWeChatView(WeChatView):

    lib = WeChatLib(WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET)

    handlers = [
        HelpOrSubscribeHandler, UnbindOrUnsubscribeHandler, AccountBindHandler,
        ViewPersonalInformationHandler, CourseSearchHandler, CourseListHandler,
        CommunicateHandler, NoticePanelHandler, LibraryRemainsHandler,
        MyCalendarHandler, SchoolCalendarHandler, NavigationHandler
    ]

    error_message_handler = ErrorHandler
    default_handler = DefaultHandler

    event_keys = {
        'library_remains': 'LIFE_LIBRARY',
        'school_calendar': 'LIFE_SCHOOL_CALENDAR',
        'navigation': 'LIFE_NAVIGATION'
    }

    # define url
    event_urls = {
        'help': 'welcome/help',
        'account_bind': 'welcome/account_bind',
        'search_course': 'learn/search_course',
        'course_list': 'learn/course_list',
        'communication': 'learn/communication',
        'notice_panel': 'learn/notice_panel',
        'calendar': 'life/calendar'
    }

    menu = {
        'button': [
            {
                'name': '欢迎',
                'sub_button': [
                    {
                        'type': 'view',
                        'name': '帮助',
                        'url': get_url(event_urls['help'])
                    },
                    {
                        'type': 'view',
                        'name': '绑定账号',
                        'url': get_redirect_url(event_urls['account_bind'])
                    }
                ]
            },
            {
                'name': '爱学习',
                'sub_button': [
                    {
                        'type': 'view',
                        'name': '课程搜索',
                        'url': get_redirect_url(event_urls['search_course'])
                    },
                    {
                        'type': 'view',
                        'name': '本人课程',
                        'url': get_redirect_url(event_urls['course_list'])
                    },
                    {
                        'type': 'view',
                        'name': '师生交流',
                        'url': get_redirect_url(event_urls['communication'])
                    },
                    {
                        'type': 'view',
                        'name': '公告及作业',
                        'url': get_redirect_url(event_urls['notice_panel'])
                    }
                ]
            },
            {
                'name': '乐生活',
                'sub_button': [
                    {
                        'type': 'click',
                        'name': '文图查座',
                        'key': event_keys['library_remains']
                    },
                    {
                        'type': 'view',
                        'name': '个人日历',
                        'url': get_redirect_url(event_urls['calendar'])
                    },
                    {
                        'type': 'click',
                        'name': '校历查询',
                        'key': event_keys['school_calendar']
                    },
                    {
                        'type': 'location_select',
                        'name': '校园导航',
                        'key': event_keys['navigation']
                    }
                ]
            }
        ]
    }

    @classmethod
    def get_book_btn(cls):
        return cls.menu['button'][-1]

    @classmethod
    def update_menu(cls):
        return cls.lib.set_wechat_menu(cls.menu)
