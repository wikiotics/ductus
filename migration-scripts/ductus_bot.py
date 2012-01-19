#!/usr/bin/env python
import optparse
import sys
import re
import os
import httplib, urllib, urllib2
import cookielib
import itertools
import mimetools
import mimetypes
import StringIO
import json
from zipfile import ZipFile
from lxml import etree, objectify


class DuctusBot(object):
    """A basic bot class that provides standard functions to interact with a
    ductus site.
    Note: if /en/main_page does not exist, this bot will not work
    (e.g. login() will fail, etc...). Set some content for the mainpage to
    solve the problem.
    """
    def __init__(self, server):
        """server: base url to the ductus as a string"""
        self.server = server
        self.crsf_token = False
        self.sessionid = None

    def get_cookies(self):
        # Set up initial cookies
        print "Getting session id and csrf token from server %s ..." % self.server
        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.opener.open(self.server + '/login').read() # make sure we read the whole response from the server, otherwise socket is invalid for further requests
        for cookie in self.cj:
            if cookie.name == 'csrftoken':
                self.csrf_token = cookie.value
                print "GOT CSRF token"
                break
        else:
            print "Couldn't get csrf token"

    def login(self, username, password):
        print "logging in..."
        values = {"csrfmiddlewaretoken": self.csrf_token,
                    "username": username,
                    "password": password}
        data = urllib.urlencode(values)
        request = urllib2.Request(self.server + '/login')
        request.add_header('User-agent', 'DuctusBot')
        request.add_header('X-CSRFToken', self.csrf_token)
        request.add_header('Cookie', 'csrftoken=' + self.csrf_token)
        request.add_header('Content-type', 'application/x-www-form-urlencoded; charset=UTF-8')
        request.add_header('Content-length', len(data))
        request.add_data(data)
        try:
            fullurl = self.opener.open(request)
        except urllib2.HTTPError as e:
            if e.code == 403:
                print "Access denied, giving up here - maybe a CSRF issue?"
                print e.read()
                sys.exit()
            if e.code == 500:
                print e.read()
                raise
        except urllib2.URLError as e:
            print "Connection failed: "
            print e.read()
        else:
            for cookie in self.cj:
                if cookie.name == 'sessionid':
                    self.sessionid = cookie.value
                    print "Login OK"

    def page_exists(self, url):
        """Check if a given url exists on the server (by checking for 404 http code). Returns a bool."""
        try:
            print "Checking availability of title: %s on server %s ..." % url, self.server
            conn = httplib.HTTPConnection(self.server)
            conn.request("HEAD", url)
            return conn.getresponse().status == 404
        except StandardError:
            raise

    def upload_audio(self, filename, file_contents=None, file_path=''):
        """Save file_contents under filename to a urn on the server. Returns the urn under which the file was saved, as a dict.
        filename: (local) name of the file to upload
        file_contents: the contents of the file as returned by File.read(). If omitted, the function will attempt to open <filename> and read its contents.
        file_path: if file_contents is None, provide file_path to filename so the function can open it (defaults to current directory). Ignored if file_contents is provided.
        """
        params = urllib.urlencode({'name': 'file', 'filename': filename})
        headers = {"Content-type": "multipart/form-data",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
        url = self.server + '/new/audio'

        if file_contents == None:
            with open(os.path.join(file_path, filename)) as f:
                file_contents = f.read()

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
        body += file_contents
        body += crlf + '--' + part_boundary + '--'
        body += crlf

        request = urllib2.Request(url)
        request.add_header('User-agent', 'DuctusBot')
        request.add_header('X-Requested-With', 'XMLHttpRequest')
        request.add_header('X-CSRFToken', self.csrf_token)
        request.add_header('Cookie', 'csrftoken=' + self.csrf_token + '; sessionid=' + self.sessionid)
        request.add_header('Content-type', 'multipart/form-data; boundary=%s' % part_boundary)
        request.add_header('Content-length', len(body))
        request.add_data(body)
        try:
            url = self.opener.open(request)
        except urllib2.HTTPError as e:
            print e.read()
            if e.code == 403:
                print "Access denied, giving up here - maybe a CSRF issue?"
                sys.exit()
            return '{"urn":""}'
        except urllib2.URLError as e:
            print "Connection failed: " + str(e)
            return '{"urn":""}'
        else:
            response = json.loads(url.read())
            return response

    def save_blueprint(self, url, blueprint, log_message=u'bot action'):
        """Save a blueprint to a urn on the server.
        url: url to save the blueprint to, without server name (e.g: "/en/my_lesson")
        blueprint: string representation of the json blueprint
        log_message: the ductus log message to record with the change
        Returns the urn under which the blueprint has been saved"""
        fullurl = self.server + url

        values = {'log_message': log_message,
                    'blueprint': blueprint.encode('utf-8')}
        data = urllib.urlencode(values, True)

        request = urllib2.Request(fullurl)
        request.add_header('User-agent', 'DuctusBot')
        request.add_header('X-Requested-With', 'XMLHttpRequest')
        request.add_header('X-CSRFToken', self.csrf_token)
        request.add_header('Cookie', 'csrftoken=' + self.csrf_token + '; sessionid=' + self.sessionid)
        request.add_header('Content-type', 'application/x-www-form-urlencoded; charset=UTF-8')
        request.add_header('Content-length', len(data))
        request.add_data(data)
        print "Connecting to %s..." % fullurl
        try:
            fullurl = self.opener.open(request)
        except urllib2.HTTPError as e:
            if e.code == 403:
                print "Access denied, giving up here - maybe a CSRF issue?"
                print e.read()
                sys.exit()
            if e.code == 500:
                raise
        except urllib2.URLError as e:
            print "Connection failed: " + str(e)
            raise
        else:
            response = json.loads(fullurl.read())
            return response

def main():
    usage = "usage: %prog [options] "
    p = optparse.OptionParser(usage=usage)
    options, arguments = p.parse_args()
    if len(arguments) != 5:
        p.print_help()
        sys.exit()


if __name__ == '__main__':
    main()
