from wechat.wrapper import WeChatView, WeChatLib
from wechat.handlers import *
from wechat.models import *
from XuetangPlus.settings import WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET
from XuetangPlus.settings import get_url, get_redirect_url
from XuetangPlus.settings import event_keys, event_urls


class CustomWeChatView(WeChatView):

    lib = WeChatLib(WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET)

    handlers = [
        HelpOrSubscribeHandler, UnbindOrUnsubscribeHandler, AccountBindHandler,
        ViewPersonalInformationHandler, CourseSearchHandler, CourseListHandler,
        CommunicateHandler, NoticePanelHandler, LibraryRemainsHandler,
        MyCalendarHandler, SchoolCalendarHandler, NavigationHandler, RemindHandler
    ]

    error_message_handler = ErrorHandler
    default_handler = DefaultHandler

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
                        'name': '绑定学号',
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
                        'name': '个人课程',
                        'url': get_redirect_url(event_urls['course_list'])
                    },
                    {
                        'type': 'view',
                        'name': '课程讨论',
                        'url': get_redirect_url(event_urls['communication_list'])
                    },
                    {
                        'type': 'view',
                        'name': '课程评价',
                        'url': get_redirect_url(event_urls['comment_list'])
                    },
                    {
                        'type': 'view',
                        'name': '通知面板',
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
                        'type': 'view',
                        'name': '校园导航',
                        'url': get_redirect_url(event_urls['navigation'])
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
