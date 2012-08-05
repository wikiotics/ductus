# docs at https://docs.djangoproject.com/en/dev/topics/testing/#live-test-server
# and http://docs.ductus.us/en/latest/testing.html#frontend-testing-javascript

from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver as FFDriver

class JSTestCase(LiveServerTestCase):
    """base class for javascript test cases (using selenium)"""

    @classmethod
    def setUpClass(cls):
        cls.selenium = FFDriver()
        super(JSTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(JSTestCase, cls).tearDownClass()
        cls.selenium.quit()
