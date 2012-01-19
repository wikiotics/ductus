import pickle
import json
import optparse
import sys
import re
import urllib
import urllib2
import string
from ductus_bot import DuctusBot    # FIXME: this relies on ln -s ../ductus_bot, clean this up!!
import os
import glob

"""
A bot to import FSI audio lessons to wikiotics.
Run without arguments to get help.

inifile format: (include the curly braces {})
{
"username": "USERNAME",
"password": "PASSWORD",
"server": "http://localhost:8000",
"filename_pattern": "*.ogg",
"target_language": "fr"
}
"""

class FSIbot(DuctusBot):

    def get_audio_files(self, path, pattern):
        """ return a list of audio files with names matching pattern contained in path.
        The list is sort according to numbered filenames, which are assumed of the form
        path/to/folder/NNN-filename with NNN being digits"""
        file_list = glob.glob(os.path.join(path, pattern))

        file_list.sort(key=lambda x: int(re.search(r'\/(\d+?)-', x).group(1)))
        for infile in file_list:
            print "adding file to list: " + infile
        return file_list

    def build_fsi_row(self, audio_file, language_code):
        """return a blueprint for a flashcard row containing audio_file"""
        print "Uploading audio file: " + audio_file
        try:
            response = self.upload_audio(audio_file, None, '.')
            urn = response['urn']
            print "Saved urn: " + urn
        except KeyError as e:
            print "Error(s) occurred while upload an audio file."
            print json.dumps(response['errors'])
            sys.exit()
        except:
            print "Failed to upload audio file. Aborting."
            raise

        bp = '{"resource":{"sides":{"array":['
        bp += '{"resource":null},'
        bp += '{"href":"' + urn + '"},'
        #bp += '{"resource":{"@create":"{http://wikiotics.org/ns/2011/phrase}phrase", "phrase":{"text":"' + language_code + '"}}},'
        bp += '{"resource":null}'
        bp += ']},"tags": {"array": [{"value": "language:'+language_code+'"}, {"value":"fsi"}]},'
        bp += '"@create":"{http://wikiotics.org/ns/2011/flashcards}flashcard"}}'
        return bp

    def build_fsi_lesson(self, file_list, language_code):
        """return a blueprint for a template lesson containing all the audio files in file_list"""
        bp_header = '{"resource":{"cards":{"array":['
        bp_footer = ']},'
        bp_footer += '"headings":{"array":[{"text":"phrase"},{"text":"audio"},{"text":"speaker"}]},'
        #bp_footer += '"headings":{"array":[{"text":"phrase"},{"text":"audio"},{"text":"language"},{"text":"speaker"}]},'
        bp_footer += '"tags": {"array": [{"value": "source-language:en"}, {"value": "target-language:'+language_code+'"}, {"value": "fsi"}]},'
        bp_footer += '"interactions":{"array":[{"resource":{"audio":"1","transcript":"0","@create":"{http://wikiotics.org/ns/2011/flashcards}audio_lesson_interaction"}}]},'
        bp_footer += '"@create":"{http://wikiotics.org/ns/2011/flashcards}flashcard_deck"}}'

        bp_body = ''
        for audio_file in file_list:
            bp_body += self.build_fsi_row(audio_file, language_code) + ','

        blueprint = bp_header + bp_body.rstrip(',') + bp_footer
        return blueprint

    def save_fsi_lesson(self, url, blueprint):
        """save the blueprint to a ductus server.
        Audio files linked to must have been uploaded to server before calling this.
        """
        urn_json = self.save_blueprint(url, blueprint, u'Import FSI audio')
        return urn_json

def main():
    usage = "usage: %prog folder lesson_url"
    p = optparse.OptionParser(usage=usage)
    p.add_option('-i', '--init-file', dest="inifile_name", help='use init file FILE (see fsi_import.py for format)', metavar="FILE")
    options, arguments = p.parse_args()
    if len(arguments) != 2:
        p.print_help()
        sys.exit()
    folder = arguments[0]
    url = arguments[1]

    try:
        # load and parse init file
        inifile = open(options.inifile_name, 'r')
        #settings = json.loads(json.dumps(json.load(inifile), ensure_ascii=True))
        settings = json.load(inifile)
        inifile.close()
    except:
        raise

    # FIXME: getting UnicodeDecodeError as soon as any of the settings are used (encode('ascii') makes it work, but why ???
    fsibot = FSIbot(settings['server'].encode('ascii'))
    try:
        fsibot.get_cookies()
        fsibot.login(settings['username'].encode('ascii'), settings['password'].encode('ascii'))
        file_list = fsibot.get_audio_files(folder, settings['filename_pattern'].encode('ascii'))
        blueprint = fsibot.build_fsi_lesson(file_list, settings['target_language'].encode('ascii'))
        fsibot.save_fsi_lesson(url, blueprint)
    except:
        raise
    #finally:

if __name__ == '__main__':
    main()
