from django.test import TestCase
from django.test.client import Client
from ductus.tests.basecase import JSTestCase

class TextwikiTests(JSTestCase):

    def test_wikitext_save_widget(self):
        # check that the save widget is present when creating a new wikitext page from scratch
        self.selenium.get('%s%s' % (self.live_server_url, '/new/wikitext'))
        w = self.selenium.find_elements_by_class_name('ductus_SaveWidget')
        assert len(w) > 0, "SaveWidget not found"

class TextWikiBackendTests(TestCase):
    def test_textwiki_save_and_view_creole_page(self):
        """send a simple creole blueprint to the server and check the resulting displayed content"""
        c = Client()
        target_url = '/hr/sometest_textpage'
        POST = {
            'blueprint': '{"resource":{"blob":{"text":"= test title =\\n* element number one\\n* element number two\\n* element number three","markup_language":"creole-1.0"},"tags":{"array":[]},"@create":"{http://wikiotics.org/ns/2009/wikitext}wikitext"}}',
            'log_message': 'created from unit tests'
        }
        response = c.post(target_url, POST, follow=True)
        self.assertRedirects(response, target_url)  # check that we got a 302 redirect plus a 200 to target_url
        self.assertContains(response, '<h1>test title</h1>', html=True)
        self.assertContains(response, '<li>element number two</li>', html=True)

    def test_textwiki_save_and_view_html5_page(self):
        """send a simple ductus-html5 blueprint to the server and check the resulting displayed content"""
        c = Client()
        target_url = '/hr/sometest_textpage'
        text = '<h1>test title</h1>\
                <p>some text in a paragraph</p>\
                <ul><li>element number one</li>\
                <li>element number two</li>\
                <li>element number three</li></ul>\
                <h2>some other heading</h2>'
        POST = {
            'blueprint': '{"resource":{"blob":{"text":"' + text + '","markup_language":"ductus-html5"},"tags":{"array":[]},"@create":"{http://wikiotics.org/ns/2009/wikitext}wikitext"}}',
            'log_message': 'created from unit tests'
        }
        response = c.post(target_url, POST, follow=True)
        self.assertRedirects(response, target_url)  # check that we got a 302 redirect plus a 200 to target_url
        self.assertContains(response, '<h1>test title</h1>', html=True)
        self.assertContains(response, '<li>element number two</li>', html=True)
