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
        'help': 'SERVICE_HELP',
    }

    menu = {
        'button': [
            {
                "name": "服务",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "帮助",
                        "key": event_keys['help'],
                    }
                ]
            }
        ]
    }
