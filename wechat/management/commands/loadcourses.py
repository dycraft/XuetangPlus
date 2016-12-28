# -*- coding: utf-8 -*-
#
import logging
import json
from wechat.models import CourseForSearch

from django.core.management.base import BaseCommand, CommandError

from wechat.views import CustomWeChatView


__author__ = "Epsirom"


class Command(BaseCommand):
    help = 'load courses'

    logger = logging.getLogger('loadcourses')

    def handle(self, *args, **options):
        CourseForSearch.objects.all().delete()
        course_data = json.load(open('./static/course/course.json', 'r'))

        length = len(course_data)
        for index, c in enumerate(course_data):
            if index % 1000 == 0:
                self.logger.info('loading: ' + str(index) + '/' + str(length))
            new_course = CourseForSearch.objects.create()
            if c['course_name'] == '':
                new_course.delete()
                continue
            new_course.course_name = c['course_name']
            new_course.course_seq = c['course_seq']
            new_course.score = c['score']
            new_course.feature = c['feature']
            new_course.intro = c['intro']
            new_course.time = c['time']
            new_course.second = c['second']
            new_course.school = c['school']
            new_course.teacher = c['teacher']
            new_course.course_id = c['course_id']
            new_course.week = c['week']
            new_course.year = c['year']
            new_course.save()

        self.logger.info('load courses complete: ' + str(length))

Command.logger.setLevel(logging.DEBUG)