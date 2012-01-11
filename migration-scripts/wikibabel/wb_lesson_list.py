import pickle
import json
import optparse
import sys
import re
import urllib
import urllib2
import string


def get_lesson(server, lang, title):
    values = {'pages': title.split('/')[-1],
                #'curonly'     : "0"}
                }
    data = urllib.urlencode(values, True)

    request = urllib2.Request(server + '/' + lang + '/Special:WBLessonExporter')
    request.add_header('User-agent', 'DuctusBot')
    request.add_header('Content-type', 'application/x-www-form-urlencoded; charset=UTF-8')
    request.add_header('Content-length', len(data))
    request.add_data(data)
    print "Connecting to %s..." % (server + title)
    try:
        fullurl = urllib2.urlopen(request)
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
        response = fullurl.read()

    # save response to zip file
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = lang + '--' + title
    filename = ''.join(c for c in filename if c in valid_chars) + '.zip'
    print filename
    local_file = open(filename, "w")
    local_file.write(response)
    local_file.close()
    return filename

def update_langcode(code):
    newcode = {
            "ara": "ar",
            "ben": "bn",
            "bod": "bo",
            "bul": "bg",
            "ces": "cs",
            "deu": "de",
            "ell": "el",
            "eng": "en",
            "fas": "fa",
            "fra": "fr",
            "ful": "ff",
            "hin": "hi",
            "hun": "hu",
            "jad": "jad",
            "kat": "ka",
            "khm": "km",
            "kor": "ko",
            "mar": "mr",
            "mon": "mn",
            "msa": "zsm",
            "pan": "pa",
            "pol": "pl",
            "por": "pt",
            "pot": "pot",
            "ron": "ro",
            "rus": "ru",
            "spa": "es",
            "swe": "sv",
            "tur": "tr",
            "ukr": "uk",
            "wol": "wo",
            "zho": "zh",
            }[code.lower()]
    return newcode

import ductus_bot

def import_lesson(filename, server, lang, link):
    trglang = re.search(r'Lesson:(.{3}):', link).group(1)
    print trglang
    trglang = update_langcode(trglang)
    title = re.search(r'Lesson:.{3}:.{1}:(.*)', link).group(1)
    print title
    archive = ductus_bot.WBLessonArchive(filename)
    importer = ductus_bot.WBimporter(server, archive, lang, trglang, title)

    while not 1: #importer.is_title_available(title):
        title = raw_input("Title not available, please choose another one: ")
        print "Lesson will be saved to " + importer.url

    importer.load_zipfile_and_register_ogg_files()
    urn = importer.create_blueprint_from_archive_XML()
    return urn


def main():
    usage = "usage: %prog wb_server_url new_server[:port] lang_code"
    p = optparse.OptionParser(usage=usage)
    options, arguments = p.parse_args()
    if len(arguments) != 3:
        p.print_help()
        sys.exit()
    wb_server = arguments[0]
    new_server = arguments[1]
    lang = arguments[2]

    url = wb_server + '/' + lang + '/Special:All_lessons'
    print "Connecting to " + url
    try:
        url = urllib2.urlopen(url)
    except urllib2.HTTPError as e:
        sys.exit()
    else:
        response = url.read()

    search_str = 'href="(/%s/Lesson:.{3}:[1-4]:.*?)"' % lang
    links = re.findall(search_str, response)

    try:
        exclude_file = open('exclude.list', 'r')
        exclude_list = pickle.load(exclude_file)
        exclude_file.close()
    except:
        exclude_list = []

    done_list = []
    match_list = []
    try:
        for link in links:
            if link in exclude_list:
                print "skipping lesson: " + link
            else:
                print "getting lesson: " + link
                filename = get_lesson(wb_server, lang, link)
                urn = import_lesson(filename, new_server, lang, link)
                done_list.append(link)
                match_list.append((wb_server + link, new_server + json.loads(urn)['page_url']))
    except:
        raise
    finally:
        # make sure we get an updated done.list
        done_list = exclude_list + done_list
        done_file = open('done.list', 'w')
        pickle.dump(done_list, done_file)
        done_file.close()
        print match_list
        match_file = open('match.list', 'w')
        pickle.dump(match_list, match_file)
        match_file.close()

if __name__ == '__main__':
    main()
