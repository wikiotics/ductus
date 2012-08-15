from ductus.tests.basecase import JSTestCase

class NewWikiPageTests(JSTestCase):

    def test_explicit_new_wikipage(self):
        """open /new/ and check that it works ok"""
        self.selenium.get('%s%s' % (self.live_server_url, '/new'))
        # disable all jQuery animations so tests won't fail waiting for them to complete
        self.selenium.execute_script('$.fx.off = true')

        # check the number of templates
        from ductus.wiki.views import _get_creation_templates, _get_creation_views
        tmplt = self.selenium.find_elements_by_class_name('ductus_creation_template')
        assert len(tmplt) == len(_get_creation_templates()), "Some creation templates missing"

        # check the number of views
        views = self.selenium.find_elements_by_css_selector('.ductus_creation_views dt')
        assert len(views) == len(_get_creation_views()), "Some creation views missing"

        # check expanding/collapsing advanced views works
        list = self.selenium.find_elements_by_class_name('ductus_creation_views')
        assert len(list) == 1
        list = list[0]
        assert list.value_of_css_property('display') == 'none'
        btn = self.selenium.find_elements_by_class_name('ductus_other_view')[0]
        btn.click()
        assert list.value_of_css_property('display') == 'block'
        btn.click()
        assert list.value_of_css_property('display') == 'none'
