# -*- coding: utf-8 -*-
#
from django.conf.urls import url

from app.views import *


urlpatterns = [
    url(r'^account/bind/?$', UserBind.as_view()),
    url(r'^map/?$', Map.as_view()),
]
