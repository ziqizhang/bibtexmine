# Use of CrossRef API
# Author @CosminP

import requests
from habanero import Crossref
import re

def download(save_folder, issn, date_start, date_end):
    cr = Crossref()

    x = cr.journals(ids=issn, works=True,
                    filter={'has_full_text': True, 'type': 'journal-article',
                            'from-pub-date': date_start, 'until-pub-date': date_end},
                    sort='issued',
                    cursor='*',
                    #mailto='ziqi.zhang@sheffield.ac.uk',
                    limit=20)

    count = 0
    articles_count = 0
    my_list = []
    total_results = x[0]['message'].get('total-results')
    total_with_pdfs = 0
    total_with_xmls = 0
    total_xml_accessible = 0
    print('total results >>>>>>>>> ', total_results)

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
            filename_xml = save_folder + title
            # filename_txt = "E:exported_data\\" + title + ".txt"

            # at index 0, the api returns nothing, so file 'empty' is just a placeholder
            # if count == 0:
            #     filename_txt = "empty"
            #     filename_xml = "empty"
            response_data = i['link']
            pdf_counted = False
            xml_counted = False
            xml_links = set()
            for d in response_data:
                content_type = d['content-type']
                if 'pdf' in content_type and not pdf_counted:
                    total_with_pdfs += 1
                    pdf_counted = True
                if 'xml' in content_type or 'html' in content_type: # or 'unspecified' in content_type:
                    response_xml = d['URL']
                    xml_links.add(response_xml)
                    if not xml_counted:
                        total_with_xmls += 1
                        xml_counted = True

            # response_xml = requests.get(i['link'][1]['URL'])

            # response_plain = requests.get((i['link'][1]['URL']) + '&apiKey=e873ab508be6a1e93c4ba6217c155ad4')

            # save the content from the xml link into a .xml file
            if len(xml_links) > 0:
                downloaded = False

                for xml in xml_links:
                    if downloaded:
                        break

                    response_xml = requests.get(xml)
                    if (response_xml.ok):
                        with open((filename_xml), 'wb+') as file:
                            # print(i['link'][1]['URL'])
                            file.write(response_xml.content)
                            downloaded = True
                            total_xml_accessible += 1
            # save the content from the text/plain link into a .txt file
            # with open((filename_txt), 'wb') as file:
            #     if (response_plain.ok):
            #         # print(i['link'][1]['URL'])
            #         file.write(response_plain.content)
        count += 1
    print("Extraction Completed, total={}".format(total_results))
    print(
        "Total with pdf={}, xml={}, downloadable xml={}".format(total_with_pdfs, total_with_xmls, total_xml_accessible))

    return total_results, total_with_pdfs, total_with_xmls, total_xml_accessible

if __name__ == "__main__":
    outfolder = "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/JASIST/"

    # ISSN for JASIS -> issn=2330-1643 / 2330-1635  1532-2882 for print and  1532-2890 for online
    # ISSN for JDOC -> issn=0022-0418
    # ISSN for LISR -> issn=0740-8188

    issn="0022-0418"

    year_start=2008
    year_end=year_start
    month_start=1
    last_year=2019
    month_increment=2
    stop=False
    batch=1

    total=0
    pdfs=0
    xmls=0
    xml_down=0

    while not stop:
        month_end=month_start+month_increment
        if month_end>12:
            month_end=1
            year_end=year_start+1
            if year_end>last_year:
                break

        if month_start<10:
            start=str(year_start)+"-0"+str(month_start)+"-01"
        else:
            start = str(year_start) + "-" + str(month_start) + "-01"
        if month_end<10:
            end=str(year_end)+"-0"+str(month_end)+"-01"
        else:
            end = str(year_end) + "-" + str(month_end) + "-01"

        print("batch{}, start={}, end={}".format(batch, start,end))
        tt, pdf, xml, xml_d=download(outfolder, issn, start, end)

        total+=tt
        pdfs+=pdf
        xmls+=xml
        xml_down+=xml_d

        month_start=month_end
        year_start=year_end

        batch+=1

        if year_end==last_year:
            break

    print("total={}, haspdf={}, hasxml={}, xmldownloaded={}".format(total,pdfs,xmls,xml_down))


# ISSN for JASIS -> issn=2330-1643, 2330-1635 'the old ISSN for JASIST was 1532-2882 for print and  1532-2890 for online'
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

