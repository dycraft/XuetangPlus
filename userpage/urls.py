from django.conf.urls import url

from userpage.views import *


urlpatterns = [
    url(r'^welcome/account_bind/?$', AccountBind.as_view()),
    url(r'^learn/course_list/?$', CourseList.as_view()),
    url(r'^learn/notice_panel/?$', NoticePanel.as_view())
]
