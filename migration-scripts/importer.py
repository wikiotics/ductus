#!/usr/bin/env python
import optparse
import sys
import re
import httplib, urllib, urllib2
import cookielib
import itertools
import mimetools
import mimetypes
import StringIO
import json
from zipfile import ZipFile
from lxml import etree, objectify

'''this class will fail miserably for non-WB archives'''
class WBLessonArchive():
    def __init__(self, filename):
        self.filename = filename
        self.zipfile = ZipFile(self.filename, 'r')

    def get_xml(self):
        return self.zipfile.open('WBLessonExport.xml').read()

    def get_ogglist(self):
        ogglist = self.zipfile.namelist()
        ogglist.remove('WBLessonExport.xml')
        return ogglist

    def get_oggfile(self, oggfilename):
        '''return contents of the OGG file named in parameter'''
        return self.zipfile.open(oggfilename).read()

    def close():
        self.zipfile.close()

class WBimporter():

    def __init__(self, server, archive, srclang, trglang, title):
        self.server = server
        self.archive = archive
        self.srclang = srclang
        self.trglang = trglang
        self.title = title
        self.url = '/' + self.trglang + '/' + self.title
        self.csrf_token = None

        # Set up initial cookies
        print "Getting session id and csrf token from server %s ..." % self.server
        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        self.opener.open(server + '/login').read() # make sure we read the whole response from the server, otherwise socket is invalid for further requests
        for cookie in cj:
            if cookie.name == 'csrftoken':
                self.csrf_token = cookie.value
                break
        else:
            print "Couldn't get csrf token"

    def is_title_available(self, title):
        '''check that given title is available on the server, so we don't overwrite an existing lesson'''
        try:
            self.url = '/' + self.trglang + '/' + title
            print "Checking availability of title: %s on server %s ..." % self.url, self.server
            conn = httplib.HTTPConnection(self.server)
            conn.request("HEAD", self.url)
            return conn.getresponse().status == 404
        except StandardError:
            return None

    def load_zipfile_and_register_ogg_files(self):
        print "Getting list of files from archive..."
        files = self.archive.get_ogglist()

        def register_oggfile(self, filename):
            params = urllib.urlencode({'name': 'file', 'filename': filename})
            headers = {"Content-type": "multipart/form-data",
                       "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
            url = self.server + '/new/audio'
            print 'Connecting to %s' % url

            # build mime representation of the file to upload
            parts = []
            part_boundary = mimetools.choose_boundary()
            crlf = '\r\n'
            body = '--' + part_boundary
            body += crlf
            body += 'Content-Disposition: form-data; name="%s"; filename="%s"' % \
                    ("file", filename)
            body += crlf
            body += 'Content-Type: %s' % mimetypes.guess_type(filename)[0]
            body += crlf + crlf
            body += self.archive.get_oggfile(filename)
            body += crlf + '--' + part_boundary + '--'
            body += crlf

            request = urllib2.Request(url)
            request.add_header('User-agent', 'WikiBabel conversion Bot')
            request.add_header('X-Requested-With', 'XMLHttpRequest')
            request.add_header('X-CSRFToken', self.csrf_token)
            request.add_header('Cookie', 'csrftoken='+self.csrf_token)
            request.add_header('Content-type', 'multipart/form-data; boundary=%s' % part_boundary)
            request.add_header('Content-length', len(body))
            request.add_data(body)
            try:
                url = self.opener.open(request)
            except urllib2.HTTPError as e:
                print "HTTP error: " + str(e)
                if e.code == 403:
                    print "Access denied, giving up here - maybe a CSRF issue?"
                    sys.exit()
                return '{"urn":""}'
            except urllib2.URLError as e:
                print "Connection failed: " + str(e)
                return '{"urn":""}'
            else:
                response = url.read()
                return response

        self.ogg_urns = {}
        for index, oggfile in enumerate(files):
            print "Uploading file %i - %s..." % (index, oggfile)
            urn_json = register_oggfile(self, oggfile)
            urn = json.loads(urn_json)
            self.ogg_urns[oggfile] = urn['urn']
            print "OGG: "+ oggfile +" - URN: " + self.ogg_urns[oggfile]

    def create_blueprint_from_archive_XML(self):
        # load XML and correct mediawiki content tags
        xml_text = unicode(self.archive.get_xml(), 'utf-8')
        xml_text = xml_text.replace('&lt;', '<')
        xml_text = xml_text.replace('&gt;', '>')
        xml_text = xml_text.replace('&quot;', '"')
        # dump namespace declarations to make subsequent processing easier
        xml_text = re.sub(r'<mediawiki(.*)>', '<mediawiki>', xml_text, 1)
        xml_tree = etree.XML(xml_text)
        wikitext = xml_tree.xpath('//wikibabel')[0]
        context = etree.iterwalk(wikitext, events=("start", "end"))
        for action, elem in context:
            if action == "end" and elem.tag in ['text', 'source', 'target']:
                elem.text = elem.text.replace('"', '\\"')
                urn = elem.get("sound")
                if urn != '':
                    elem.set("sound", self.ogg_urns[urn + '.ogg'])
        return self.do_xslt(wikitext)

    def do_xslt(self, tree):
        xslt = etree.parse("wb_to_json.xsl")
        transform = etree.XSLT(xslt)
        json_blueprint = unicode(transform(tree, source_language="'"+self.srclang+"'", target_language="'"+self.trglang+"'"))
        json_blueprint = json_blueprint.replace('\n', '')
        # FIXME: ugly workaround to XSL stylesheet: remove the last ',' separator between templates. Ideally XSL stylesheet should be corrected :)
        json_blueprint = json_blueprint.replace('flashcard"}},]}', 'flashcard"}}]}')
        json_test = json.loads(json_blueprint)
        return json.dumps(json_test)

    def save_blueprint(self, blueprint):
        url = self.server + self.url

        values = {'log_message': 'Import from wiki-babel.org',
                    'blueprint': blueprint}
        data = urllib.urlencode(values, True)

        request = urllib2.Request(url)
        request.add_header('User-agent', 'WikiBabel conversion Bot')
        request.add_header('X-Requested-With', 'XMLHttpRequest')
        request.add_header('X-CSRFToken', self.csrf_token)
        request.add_header('Cookie', 'csrftoken='+self.csrf_token)
        request.add_header('Content-type', 'application/x-www-form-urlencoded; charset=UTF-8')
        request.add_header('Content-length', len(data))
        request.add_data(data)
        print "Connecting to %s..." % url
        try:
            url = self.opener.open(request)
        except urllib2.HTTPError as e:
            print "HTTP error: " + str(e)
            if e.code == 403:
                print "Access denied, giving up here - maybe a CSRF issue?"
                sys.exit()
            if e.code == 500:
                print url.read()
        except urllib2.URLError as e:
            print "Connection failed: " + str(e)
        else:
            response = url.read()
            return response


class objectJSONEncoder(json.JSONEncoder):
    def __init__(self):
        return json.JSONEncoder(False, False)

    def default(self, o):
        if isinstance(o, objectify.ObjectifiedElement) and o.countchildren() > 1:
            '''ensure that all children with same name get converted'''
            return [child for child in o.iterchildren()]
        if isinstance(o, objectify.IntElement):
            return int(o)
        if isinstance(o, objectify.NumberElement) or isinstance(o, objectify.FloatElement):
            return float(o)
        if isinstance(o, objectify.ObjectifiedDataElement):
            return str(o)
        if hasattr(o, '__dict__'):
            return o.__dict__
        return json.JSONEncoder.default(self, o)

def main():
    usage = "usage: %prog [options] server zipfile source_language target_language lesson_title"
    p = optparse.OptionParser(usage=usage)
    #p.add_option('-c', '--csrf-token', help='use CSRF-token')
    options, arguments = p.parse_args()
    if len(arguments) != 5:
        p.print_help()
        sys.exit()
    server = arguments[0]
    archive = WBLessonArchive(arguments[1])
    srclang = arguments[2]
    trglang = arguments[3]
    title = arguments[4]
    importer = WBimporter(server, archive, srclang, trglang, title)

    while not 1: #importer.is_title_available(title):
        title = raw_input("Title not available, please choose another one: ")
    print "Lesson will be saved to " + importer.url

    importer.load_zipfile_and_register_ogg_files()
    blueprint = importer.create_blueprint_from_archive_XML()
    print importer.save_blueprint(blueprint)

if __name__ == '__main__':
    main()
