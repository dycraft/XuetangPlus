from django.db import models

from codex.baseerror import LogicError


class User(models.Model):
    #open_id = models.CharField(max_length=64, unique=True, db_index=True)
    student_id = models.CharField(max_length=32, unique=True, db_index=True)
    username = models.CharField(max_length=32, unique=True, db_index=True)
    department = models.CharField(max_length=64, db_index=True, default='')
    position = models.CharField(max_length=32, db_index=True, default='')
    email = models.CharField(max_length=32, db_index=True, default='')
    realname = models.CharField(max_length=32, db_index=True, default='')

    @classmethod
    def get_by_openid(cls, openid):
        try:
            return cls.objects.get(open_id=openid)
        except cls.DoesNotExist:
            raise LogicError('User not found')
