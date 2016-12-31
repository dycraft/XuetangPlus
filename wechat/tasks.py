#encoding=UTF-8
from __future__ import absolute_import

from celery import task
from wechat.models import User, WechatConfirmation
from wechat.message_models import *
import json
import requests
from util.time import *
from codex.baseerror import LogicError


@task
def remind_informations():
    #print("remind")
    users = User.objects.all()

    confirm = WechatConfirmation.objects.get(id=1)

    for user in users:
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
        model = message_model.create_remind_model(user.open_id, hw_num, info_num, timenow)

        model_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=';
        model_url += confirm.get_access_token()
        res = requests.post(model_url, data=json.dumps(model))