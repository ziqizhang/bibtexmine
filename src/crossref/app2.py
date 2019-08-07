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
x = cr.journals(ids = "0740-8188", works =True,
                filter = {'has_full_text':True, 'type': 'journal-article', 'from-pub-date':'2008-01-01', 'until-pub-date':'2008-03-03'},
                sort='issued',
                cursor='*',
                limit=20)
# details of a doi
# y = cn.content_negotiation(ids="10.1002/asi.24193")
count=0

for i in x['message']['items']:

    # get the title and remove any special characters, keep spaces
    # title = re.sub('[^A-Za-z0-9]+', '', str(x['message']['items'][count]['title'][0])[:85])
    title = re.sub('[^A-Za-z0-9]+', ' ', (i.get('title')[0]))
    filename_xml = "E:exported_data\\" + title + ".xml"
    filename_txt = "E:exported_data\\" + title + ".txt"

    count += 1
    print(count)
    # at index 0, the api returns nothing, so file 'empty' is just a placeholder
    if count==0:
        filename_txt = "empty"
        filename_xml = "empty"

    # print all links available for the given article iteration "i"
    print(i.get('link'))
    # print the title of the article
    # print(x['message']['items'][count]['title'])

    # pass in the api key and combine with the api link
    response_xml = requests.get((i['link'][0]['URL']) + '&apiKey=e873ab508be6a1e93c4ba6217c155ad4')
    response_plain = requests.get((i['link'][1]['URL']) + '&apiKey=e873ab508be6a1e93c4ba6217c155ad4')

    # save the content from the xml link into a .xml file
    with open((filename_xml), 'wb+') as file:
        if (response_xml.ok):
            # print(i['link'][1]['URL'])
            file.write(response_xml.content)
    # save the content from the text/plain link into a .txt file
    with open((filename_txt), 'wb') as file:
        if (response_plain.ok):
            # print(i['link'][1]['URL'])
            file.write(response_plain.content)
file.close()
print("Total number of files is ", count)