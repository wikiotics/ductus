from ductus.tests.basecase import JSTestCase

class FlashcardDeckTests(JSTestCase):
    fixtures = ['user-data.json']

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

    def test_fcd_template_podcast(self):
        # check that the template is created (make sure we have 3 columns with the right titles)
        self.selenium.get('%s%s' % (self.live_server_url, '/new/flashcard_deck?template=podcast'))
        w = self.selenium.find_elements_by_class_name('ductus_FlashcardDeck_column')
        assert len(w) == 3, "Podcast template broken: wrong number of columns"

    def test_fcd_template_podcast_tag(self):
        # check that the template is created with preset tag given in url
        tagname = 'sometag'
        self.selenium.get('%s%s' % (self.live_server_url, '/new/flashcard_deck?template=podcast&tag=' + tagname))
        w = self.selenium.find_elements_by_css_selector('li.token-input-token p')
        assert len(w) == 1, "preset tags not loading"
        text = self.selenium.execute_script('return $("li.token-input-token p").text()')
        assert text == tagname

    def test_fcd_add_row_button(self):
        # check that the bottom left add row button creates a new row when clicked
        self.selenium.get('%s%s' % (self.live_server_url, '/new/flashcard_deck'))
        button = self.selenium.find_elements_by_class_name('ductus_add_row')
        assert len(button) == 1
        button = button[0]
        rows = self.selenium.find_elements_by_class_name('ductus_Flashcard')
        assert len(rows) == 1
        for i in range(6):
            button.click()
            rows = self.selenium.find_elements_by_class_name('ductus_Flashcard')
            assert len(rows) == i + 2
