from ductus.tests.basecase import JSTestCase

class TextwikiTests(JSTestCase):

    def test_wikitext_save_widget(self):
        # check that the save widget is present when creating a new wikitext page from scratch
        self.selenium.get('%s%s' % (self.live_server_url, '/new/wikitext'))
        w = self.selenium.find_elements_by_class_name('ductus_SaveWidget')
        assert len(w) > 0, "SaveWidget not found"
