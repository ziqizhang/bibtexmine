# Use of CrossRef API
# Author @CosminP

import json
import requests
from crossref.restful import Works, Journals
from habanero import Crossref

works = Works()
journals = Journals()
cr = Crossref()


# res = cr.works(facet="issn:2330-1643")
# x = cr.works(filter = {'has_full_text':True})
# print(x)


# # Jasist ISSN lookout
# url = 'http://api.crossref.org/journals/2330-1643'
# # url = 'http://api.crossref.org/journals/2330-1643/works?select=DOI'
# #
# myResponse = requests.get(url)
#
# if(myResponse.ok):
#     jsonData = json.loads(myResponse.content)
#     print(sorted(jsonData['message']['breakdowns']['dois-by-issued-year']))



# for i in works.filter(has_full_text='true', has_license='true', from_pub_date ='2009-04-04', until_pub_date='2010-04-04').sample(5).select('title','DOI'):
#     print(i)

# for i in journals.works(23301643).filter(has_full_text='true').sample(2).select('title','DOI','link'):
#     print (i)
#empty c
# for i in journals.works(23301643).filter(has_full_text='true').sample(2).select('link'):
#     print (i)

# x = journals.works(journals.works(23301643).filter(has_full_text='true'))
# # get doi for each item
# [z['DOI']for z in x['message']['items'] ]

#CrossRef api struct
## get doi and url for each item
# [ {"doi": z['DOI'], "url": z['URL']}forzinx['message']['items'] ]
# for i in works.query(bibliographic='23301643').filter(has_full_text='true').sample(5).select('title','DOI'):
#     print(i)


# # habanero to get DOIs of publications with full-text available by ISSN
# y = cr.works(facet='issn:2330-1643', filter = {'has_full_text':True}, cursor = "*", cursor_max = 10)
# collected_dois = [z['DOI'] for z in y['message']['items']]
# print(collected_dois)

# habanero -> select from JASIST only articles with full-text available
# limited to ~20, use cursor for deep paging
# x = cr.works(facet='issn:2330-1643', filter={'has_full_text':True, 'type': 'journal-article', 'from-pub-date':'2008-01-01','until-pub-date':'2018-01-01'},
#              query="JASIST",
#              limit=5)
x = cr.works(filter={'has_full_text':True, 'type': 'journal-article', 'from-pub-date':'2008-01-01','until-pub-date':'2018-01-01'},
             query="JASIST",
             limit=5)

# count = 0
# for i in x['message']['items']:
# # get doi
# # % of pdfs
#     # print out the links in diff formats by index
#     # print(i['link'][0]['URL'])
#     # xml to text
#     # abstracts to export
#     print("Item ", i['link'])
#     # write the contents of the links in a file
#     with open('collection.xml', 'wb') as file:
#         response = requests.get(i['link'][0]['URL'])
#         if(response.ok):
#             count += 1
#             response = requests.get(str(i['link'][0]['URL']))
#             print(response)
#             file.write(response.content)
#     link = i['link']
#     if ("pdf" in link):
#         print("PDF FILE")
#     # elif(link.find("xml")>1):
#     #     print("XML FILE")
#     # elif(link.find("plain")>1):
#     #     print("Plain text file")
#
# file.close()
# print("Written ", count, " xml files into collections.xml")