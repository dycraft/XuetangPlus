from wechat.wrapper import WeChatView, WeChatLib
from wechat.handlers import *
from wechat.models import *
from XuetangPlus.settings import WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET


class CustomWeChatView(WeChatView):

    lib = WeChatLib(WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET)

    handlers = [
        HelpOrSubscribeHandler,
    ]

    error_message_handler = ErrorHandler
    default_handler = DefaultHandler

    event_keys = {
        'help': 'WELCOME_HELP',
        'account_bind': 'WELCOME_BIND'
    }

    menu = {
        'button': [
            {
                "name": "欢迎",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "帮助",
                        "key": event_keys['help'],
                    },
                    {
                        "type": "click",
                        "name": "绑定账号",
                        "key": event_keys['account_bind'],
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
