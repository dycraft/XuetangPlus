from django.conf.urls import url

from userpage.views import *


urlpatterns = [
    url(r'^welcome/account_bind/?$', AccountBind.as_view()),
]
