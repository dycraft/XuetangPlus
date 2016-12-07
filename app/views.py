from codex.baseerror import *
from codex.baseview import APIView
from wechat.models import User
import requests
import json
from wechat.wrapper import WeChatLib
from XuetangPlus.settings import WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET

class UserBind(APIView):

    def validate_user(self):
        """
        input: self.input['student_id'] and self.input['password']
        raise: ValidateError when validating failed
        """
        dic = {'username': str(self.input['username']),
               'password': str(self.input['password'])}
        response = requests.post('http://se.zhuangty.com:8000/users/register', json = dic)
        if response.status_code == 200:
            res = json.loads(response.content.decode())
            user = User.get_by_openid(self.input['openid'])
            user.username = res['username']
            user.student_id = res['information']['studentnumber']
            user.department = res['information']['department']
            user.position = res['information']['position']
            user.email = res['information']['email']
            user.realname = res['information']['realname']
            user.save()
            return True
        raise NotImplementedError('username/student_id or password error')

    def get(self):
        self.check_input('openid')
        return User.get_by_openid(self.input['openid']).student_id

    def post(self):
        self.check_input('openid', 'username', 'password')
        self.validate_user()

class Map(APIView):
    lib = WeChatLib(WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET)

    def get(self):
        if 'type' in self.input:
            params = self.input
            ans = self.lib.changeLocationIndex(params['lati'], params['longi'], params['type'])
            return ans
        elif 'keyword' in self.input:
            params = self.input
            ans = self.lib.getRecommendAddress(params['keyword'])
            return ans
        access_token = self.lib.get_wechat_access_token()
        ticket = self.lib.get_wechat_jsapi_ticket()
        answer = [('access_token', access_token), ('ticket', ticket)]
        result = json.dumps(dict(answer))
        print("get all tickets")

        return result

    def post(self):
        return
