# -*- coding: utf-8 -*-
#
import logging

from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError

from wechat.views import CustomWeChatView


__author__ = "Epsirom"


class Command(BaseCommand):
    help = 'Automatically synchronize WeChat menu'

    logger = logging.getLogger('syncmenu')

    def handle(self, *args, **options):
        CustomWeChatView.update_menu()
        act_btns = CustomWeChatView.get_book_btn().get('sub_button', list())
        self.logger.info('Updated %d activities', len(act_btns))
        self.logger.info('=' * 32)
        for idx, act in enumerate(act_btns):
            self.logger.info('%d. %s (%s)', idx, act.get('name', ''), act.get('key', ''))


Command.logger.setLevel(logging.DEBUG)
