# Use of CrossRef API
# Author @CosminP

import json
import requests
from crossref.restful import Works, Journals
from habanero import Crossref
import os.path
import re


works = Works()
journals = Journals()
cr = Crossref()

# ISSN for JASIS -> issn=2330-1643
# ISSN for JDOC -> issn=0022-0418
# ISSN for LISR -> issn=0740-8188
# x = cr.journals(ids = "0740-8188", works =True,
#                 filter = {'has_full_text':True, 'type': 'journal-article', 'from-pub-date':'2008-01-01', 'until-pub-date':'2018-01-01'},
#                 sort='issued',
#                 cursor='*',
#                 cursor_max=1000,
#                 limit='200')
# details of a doi
# y = cn.content_negotiation(ids="10.1002/asi.24193")
# DONE SO FAR: 2008-01-01 -> 2010-01-01#, '2010-01-01 -> 2012-01-01, 2012-01-01 -> 2014-01-01, 2014-01-01 -> 2016-01-01, 2016-01-01 -> 2018-01-01

x = cr.journals(ids = "2330-1643", works =True,
                filter = {'has_full_text':True, 'type': 'journal-article',
                          'from-pub-date':'2016-01-01', 'until-pub-date':'2019-01-01'},
                sort='issued',
                cursor='*',
                limit=20)

count = 0
articles_count = 0
my_list = []
total_results = x[0]['message'].get('total-results')
print('total results >>>>>>>>> ' , total_results)

while (articles_count < total_results):
    for i in x[count]['message']['items']:
        # get the title and remove any special characters, keep spaces
        # title = re.sub('[^A-Za-z0-9]+', '', str(x['message']['items'][count]['title'][0])[:85])
        articles_count += 1
        print("Article ", articles_count, " out of ", total_results)
        # print(title)
        # print(count)
        # print(articles_count)
        total_articles = len(i.get('title')[0])

        title = (re.sub('[^A-Za-z0-9]+', ' ', (i.get('title')[0]))[:85])
        filename_xml = "E:exported_data\\" + title + ".pdf"
        # filename_txt = "E:exported_data\\" + title + ".txt"

        # at index 0, the api returns nothing, so file 'empty' is just a placeholder
        # if count == 0:
        #     filename_txt = "empty"
        #     filename_xml = "empty"

        response_xml = requests.get(i['link'][1]['URL'])

        # response_plain = requests.get((i['link'][1]['URL']) + '&apiKey=e873ab508be6a1e93c4ba6217c155ad4')

        # save the content from the xml link into a .xml file
        with open((filename_xml), 'wb+') as file:
            if (response_xml.ok):
                # print(i['link'][1]['URL'])
                file.write(response_xml.content)
        # save the content from the text/plain link into a .txt file
        # with open((filename_txt), 'wb') as file:
        #     if (response_plain.ok):
        #         # print(i['link'][1]['URL'])
        #         file.write(response_plain.content)
    count += 1
print("Extraction Completed.")