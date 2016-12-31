from django.test import LiveServerTestCase
from selenium import webdriver
from XuetangPlus import settings
from XuetangPlus.settings import event_urls
import time


class FunctionalTest(LiveServerTestCase):
    browser = None

    @classmethod
    def setUpClass(cls):
        super(FunctionalTest, cls).setUpClass()
        cls.browser = webdriver.PhantomJS()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(FunctionalTest, cls).tearDownClass()

    def test_index(self):
        url = settings.get_redirect_url(event_urls['search_course'])
        self.browser.get('%s' % url)
        self.browser.set_window_size(512, 768)
        time.sleep(10)
        self.browser.get_screenshot_as_file('课程搜索.png')
