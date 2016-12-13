from django.test import TestCase
from util.time import *
from django.utils import timezone

class TimeF2B2FTestCase(TestCase):

    def test_type_str(self):
        test = timezone.now()
        self.assertEqual(type(time_b2f(test)), str)

    def test_type_datetime(self):
        test = '1970-01-01T00:00:01.0Z'
        self.assertEqual(type(time_f2b(test)), datetime.datetime)

    def test_true_with_str(self):
        f1 = '1970-01-01T00:00:01.0Z'
        b = time_f2b(f1)
        f2 = time_b2f(b)
        self.assertEqual(f2, '1.0')


class TimeB2WTestCase(TestCase):

    def test_type_str(self):
        test = timezone.now()
        self.assertEqual(type(time_b2w(test)), str)

    def test_true_with_datetime(self):
        test = datetime.datetime.fromtimestamp(0)
        self.assertEqual(time_b2w(test), '1970-01-01 08:00')
