import pickle
import json
import optparse
import sys
import re
import urllib
import urllib2
import string
from ductus_bot import DuctusBot    #FIXME: this relies on ln -s ../ductus_bot, clean this up!!
import os
import glob

"""
A bot to import FSI audio lessons to wikiotics.
Run without arguments to get help.
"""

class FSIbot(DuctusBot):

    def get_audio_files(self, path, pattern):
        """ return a list of audio files with names matching pattern contained in path.
        The list is sort according to numbered filenames, which are assumed of the form
        path/to/folder/NNN-filename with NNN being digits"""
        file_list = glob.glob( os.path.join(path, pattern) )
        
        file_list.sort(key=lambda x:int(re.search(r'\/(\d+?)-', x).group(1)) )
        #for infile in file_list:
        #    print "current file is: " + infile + " - " + re.search(r'\/(\d+?)-', infile).group(1)
        return file_list

    def build_fsi_row(self, audio_file, language_code):
        """return a blueprint for a flashcard row containing audio_file"""
        print "Uploading audio file: " + audio_file
        try:
            urn_json = self.upload_audio(audio_file, None, '.')
            urn = json.loads(urn_json)['urn']
            print "Saved urn: " + urn
        except:
            print "Failed to upload audio file. Aborting."
            raise
            #sys.exit()

        bp = '{"resource":{"sides":{"array":['
        bp += '{"resource":null},'
        bp += '{"href":"' + urn + '"},'
        bp += '{"resource":{"@create":"{http://wikiotics.org/ns/2011/phrase}phrase", "phrase":{"text":"' + language_code + '"}}},'
        bp += '{"resource":null}'
        bp += ']},"@create":"{http://wikiotics.org/ns/2011/flashcards}flashcard"}}'
        return bp

    def build_fsi_lesson(self, file_list, language_code):
        """return a blueprint for a template lesson containing all the audio files in file_list"""
        bp_header = '{"resource":{"cards":{"array":['
        bp_footer = ']},'
        bp_footer += '"headings":{"array":[{"text":"phrase"},{"text":"audio"},{"text":"language"},{"text":"speaker"}]},'
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
    usage = "usage: %prog server[:port] lang_code folder filename_pattern lesson_url"
    p = optparse.OptionParser(usage=usage)
    p.add_option('-i', '--init-file', help='use init file')
    options, arguments = p.parse_args()
    if len(arguments) != 5:
        p.print_help()
        sys.exit()
    server = arguments[0]
    lang = arguments[1]
    folder = arguments[2]
    file_pattern = arguments[3]
    url = arguments[4]

    print "pattern: " + file_pattern
    fsibot = FSIbot(server)

    try:
        fsibot.get_cookies()
        fsibot.login(USERNAME, PASSWORD)
        file_list = fsibot.get_audio_files(folder, file_pattern)
        blueprint = fsibot.build_fsi_lesson(file_list, lang)
        fsibot.save_fsi_lesson(url, blueprint)
    except:
        raise
    #finally:

if __name__ == '__main__':
    main()
