from django.db import models

from codex.baseerror import LogicError


class User(models.Model):
    open_id = models.CharField(max_length=64, unique=True, db_index=True)
    student_id = models.CharField(max_length=32, unique=True, db_index=True)
    username = models.CharField(max_length=32, unique=True, db_index=True, default='')
    department = models.CharField(max_length=64, default='')
    position = models.CharField(max_length=32, default='')
    email = models.CharField(max_length=32, default='')
    realname = models.CharField(max_length=32, default='')

    @classmethod
    def get_by_openid(cls, openid):
        try:
            return cls.objects.get(open_id=openid)
        except cls.DoesNotExist:
            raise LogicError('User not found')


class Course(models.Model):
    name = models.CharField(max_length=128)
    courseid = models.CharField(max_length=128)
    comments = models.CharField(max_length=1024, default='[]')


class Comment(models.Model):
    commenter = models.IntegerField()
    content = models.CharField(max_length=512, default='')
    score = models.IntegerField()

    def get_commenter_name(self):
        if self.commenter == -1:
            return 'anonymous'
        else:
            return User.objects.get(id=self.commenter)