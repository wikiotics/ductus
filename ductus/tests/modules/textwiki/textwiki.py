# docs at https://docs.djangoproject.com/en/dev/topics/testing/#live-test-server

from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver

class TextwikiTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(TextwikiTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TextwikiTests, cls).tearDownClass()
        cls.selenium.quit()

    def test_wikitext_save_widget(self):
        # check that the save widget is present when creating a new wikitext page from scratch
        self.selenium.get('%s%s' % (self.live_server_url, '/new/wikitext'))
        w = self.selenium.find_elements_by_class_name('ductus_SaveWidget')
        assert len(w) > 0, "SaveWidget not found"
