# docs at https://docs.djangoproject.com/en/dev/topics/testing/#live-test-server

from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver

class FlashcardDeckTests(LiveServerTestCase):
    fixtures = ['user-data.json']

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(FlashcardDeckTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(FlashcardDeckTests, cls).tearDownClass()
        cls.selenium.quit()

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/login'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('Ductususer')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('secret')
        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()

    def test_fcd_save_widget(self):
        # check that the save widget is present when creating a new flashcard deck from scratch
        self.selenium.get('%s%s' % (self.live_server_url, '/new/flashcard_deck'))
        w = self.selenium.find_elements_by_class_name('ductus_SaveWidget')
        assert len(w) > 0, "SaveWidget not found"

    def test_wikitext_save_widget(self):
        # check that the save widget is present when creating a new wikitext page from scratch
        self.selenium.get('%s%s' % (self.live_server_url, '/new/wikitext'))
        w = self.selenium.find_elements_by_class_name('ductus_SaveWidget')
        assert len(w) > 0, "SaveWidget not found"
