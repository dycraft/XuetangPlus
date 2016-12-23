# -*- coding: utf-8 -*-
#
from django.conf.urls import url

from userpage.views import *


urlpatterns = [
    url(r'^welcome/openid/?$', GetOpenId.as_view()),
    url(r'^welcome/account_bind/?$', AccountBind.as_view()),
    url(r'^welcome/check_bind/?$', CheckBind.as_view()),
    url(r'^welcome/unbind/?$', UnBind.as_view()),
    url(r'^learn/course_list/?$', CourseList.as_view()),
    url(r'^learn/notice_panel/notice/?$', NoticeList.as_view()),
    url(r'^learn/notice_panel/assignment/?$', AssignmentList.as_view()),
    url(r'^learn/notice_panel/slide/?$', SlideList.as_view()),
    url(r'^learn/notice_panel/me/?$', MeInfo.as_view()),
    url(r'^course/information/?$', CourseInfo.as_view()),
    url(r'^course/comment/?$', CourseComment.as_view()),
    url(r'^communicate/menu?$', ChatMenu.as_view()),
    url(r'^communicate/area?$', ChatArea.as_view()),
    url(r'^read/notice/record?$', ReadNoticeRecord.as_view()),
    url(r'^event/list?$', EventList.as_view()),
    url(r'^event/create?$', EventCreate.as_view()),
    url(r'^event/detail?$', EventDetail.as_view()),
    url(r'^jssdk/?$', GetJSSDK.as_view())
]
