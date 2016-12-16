# -*- coding: utf-8 -*-
#
from django.conf.urls import url

from userpage.views import *


urlpatterns = [
    url(r'^welcome/account_bind/?$', AccountBind.as_view()),
    url(r'^welcome/check_bind/?$', CheckBind.as_view()),
    url(r'^welcome/unbind/?$', UnBind.as_view()),
    url(r'^learn/course_list/?$', CourseList.as_view()),
    url(r'^course/information/?$', CourseInfo.as_view()),
    url(r'^course/comment/?$', CourseComment.as_view()),
    url(r'^learn/notice_panel/?$', NoticePanel.as_view()),

    url(r'^jssdk/?$', GetJSSDK.as_view())
]
