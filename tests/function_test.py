from django.test import LiveServerTestCase
from django.test import testcases
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from django.core import management
import os
import time

class UserPageTest(LiveServerTestCase):
    fixtures = ['users.json']
    browser = None

    @classmethod
    def setUpClass(cls):
        super(UserPageTest, cls).setUpClass()
        cls.browser = webdriver.PhantomJS()
        cls.username = os.environ.get('username', '')
        cls.password = os.environ.get('password', '')

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(UserPageTest, cls).tearDownClass()


    def test_bind_user(self):
        self.browser.get('%s%s' % (self.live_server_url,'/welcome/account_bind/?openid=1'))

        name_box = WebDriverWait(self.browser,3).until(
            expected_conditions.presence_of_element_located((By.ID,'inputUsername'))
        )
        name_box.send_keys("2014013421")
        '''
        password_box = self.browser.find_element_by_id('inputPassword')
        password_box.send_keys("123456")

        submit_button = self.browser.find_element_by_css_selector('#validationHolder button')
        submit_button.click()
        WebDriverWait(self.browser, 3).until(
            lambda x: '正在认证' not in self.browser.find_element_by_id('mainbody').text
        )
        self.assertIn('奇怪的错误', self.browser.find_element_by_id('mainbody').text)
        self.browser.get('%s%s' % (self.live_server_url, '/u/bind/?openid=1'))

        name_box = WebDriverWait(self.browser, 3).until(
            expected_conditions.presence_of_element_located((By.ID, 'inputUsername'))
        )
        name_box.send_keys("2014013421")

        password_box = self.browser.find_element_by_id('inputPassword')
        password_box.send_keys("xsx345997420XXMCRL")

        self.browser.get_screenshot_as_file('1234.jpg')

        submit_button = self.browser.find_element_by_css_selector('#validationHolder button')
        submit_button.click()
        WebDriverWait(self.browser, 3).until(
            lambda x: '正在认证' not in self.browser.find_element_by_id('mainbody').text
        )
        self.assertIn('认证成功', self.browser.find_element_by_id('mainbody').text)
        '''