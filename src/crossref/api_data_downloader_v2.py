import requests
from habanero import Crossref
import re

#wiley token: 91513066-669e26ee-f8011e19-1904949c https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining
#elsvier api: 3de3ea46f570812ea359fa0290497181 https://dev.elsevier.com/index.html

def download(save_folder, issn, date_start, date_end,
             api_key=None, tdm_token=None,
             arbitrary_xml_dl=False, filewriter=None):

    cr = Crossref()

    x = cr.journals(ids=issn, works=True,
                    filter={'has_full_text': True, 'type': 'journal-article',
                            'from-pub-date': date_start, 'until-pub-date': date_end},
                    sort='issued',
                    cursor='*',
                    # mailto='ziqi.zhang@sheffield.ac.uk',
                    limit=20)

    count = 0
    articles_count = 0
    total_results = x[0]['message'].get('total-results')
    total_with_pdfs = 0
    total_with_xmls = 0
    total_unspecified = 0
    total_downloaded = 0
    print('total results >>>>>>>>> ', total_results)

    while articles_count < total_results:
        for i in x[count]['message']['items']:
            articles_count += 1
            print('\tArticle {0} out of {1}'.format(articles_count, total_results))

            title = (re.sub('[^A-Za-z0-9]+', ' ', (i.get('title')[0]))[:85])  # title is sometimes too long
            # so cut it to max 85chars
            filename_xml = save_folder + title
            response_data = i['link']
            has_xml=False
            xml_links = set()

            unspecified_link=None
            if arbitrary_xml_dl:
                xml_links.add(response_data[0]['URL'])

            else:
                for d in response_data:
                    content_type = d['content-type']
                    intended=d['intended-application']
                    link=d['URL']
                    if 'xml' in content_type or 'html' in content_type or 'xml' in link or 'html' in link:
                        #print('found xml file <<<<<<<<< {}'.format(d))
                        total_with_xmls += 1
                        xml_links.add(link)  # add download link to the list
                        has_xml=True
                    if 'pdf' in str(content_type):
                        #print('found pdf file <<<<<<<<< {}'.format(d))
                        total_with_pdfs += 1
                    if 'unspecified' in str(content_type) and not has_xml and intended=='text-mining':
                        #print('found unspecified type | POSSIBLE HTML <<<<<<<<< {}'.format(d))
                        #xml_links.add(link)
                        total_unspecified += 1
            if not has_xml:
                print("\t\twarning, no xml data for {}, trying to save it as html".format(xml_links))

            # download files from the list made above
            if len(xml_links) > 0:
                downloaded = False

                set(xml_links)
                for xml in xml_links:
                    #print('----------processing xml link: {}'.format(xml))
                    if downloaded:
                        break

                    #response_xml = requests.get((i['link'][0]['URL']) + '&apiKey=e873ab508be6a1e93c4ba6217c155ad4')

                    # for LISR use the api key to get the full
                    if api_key is not None:
                        response_xml = requests.get(xml + api_key)
                    elif tdm_token is not None:
                        params={'CR-Clickthrough-Client-Token':tdm_token}
                        response_xml=requests.get(xml, params)
                    else:
                        response_xml=requests.get(xml)

                    # for jdoc it works without the key
                    #response_xml = requests.get(xml)

                    if response_xml.ok:
                        if has_xml:
                            filename_xml += '.xml'  # add termination to the file name (location+filename+ext)
                        else:
                            filename_xml+='.html'
                        with open(filename_xml, 'wb+') as file:
                            file.write(response_xml.content)
                            downloaded = True
                            if response_xml.content is not None:
                                # with open(filename_xml, 'r',encoding='utf8') as file:
                                #     if file.read() is not None:
                                total_downloaded += 1
                    else:
                        #save the link
                        print(response_xml.status_code)
                        filewriter.write(xml + "\n")
        count += 1
        # the limit of cr.journals is set to 20
        # so the api returns results in batches of 20
        # increase the count to get to next batch in x[count]['message']['items']

    print("Extraction Completed, total={}".format(total_results))
    print(
        "Total with pdf={}, xml={}, unspecified={}, downloaded={}".
            format(total_with_pdfs, total_with_xmls, total_unspecified,total_downloaded))

    return total_results, total_with_pdfs, total_with_xmls, total_downloaded, total_unspecified


if __name__ == "__main__":
    outfolder = "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/JDOC_/"
    log_file_failed='/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/JDOC_failed.log'
    apikey= None#'&apiKey=3de3ea46f570812ea359fa0290497181'
    tdm=None #'91513066-669e26ee-f8011e19-1904949c'
    force_dl=False

    # ISSN for JASIS -> issn=2330-1643 / 2330-1635  1532-2882 for print and  1532-2890 for online
    # ISSN for JDOC -> issn=0022-0418
    # ISSN for LISR -> issn=0740-8188 (2016,17)

    issn = "0022-0418"

    year_start = 2008
    year_end = year_start
    month_start = 1
    end_year = 2019
    day_end= "-01"
    month_increment = 3
    stop = False
    batch = 1

    total = 0
    pdfs = 0
    xmls = 0
    unspecified=0
    down = 0

    y_total=0
    y_pdfs=0
    y_xmls=0
    y_unspecified=0
    y_dl=0

    yearly_stats={}

    at_year_end=False
    f = open(log_file_failed, "w")
    while not stop:
        month_end = month_start + month_increment
        if month_end >= 12:
            at_year_end=True
            month_end = 12
            day_end= "-31"

        if month_start < 10:
            start = str(year_start) + "-0" + str(month_start) + "-01"
        else:
            start = str(year_start) + "-" + str(month_start) + "-01"
        if month_end < 10:
            end = str(year_end) + "-0" + str(month_end) + day_end
        else:
            end = str(year_end) + "-" + str(month_end) + day_end

        print("batch{}, start={}, end={}".format(batch, start, end))
        tt, pdf, xml, xml_d, uns = download(outfolder, issn, start, end,
                                            filewriter=f,
                                            api_key=apikey,
                                            tdm_token=tdm,
                                            arbitrary_xml_dl=force_dl)

        total += tt
        pdfs += pdf
        xmls += xml
        down += xml_d
        unspecified+=uns

        y_total += tt
        y_pdfs += pdf
        y_xmls += xml
        y_dl += xml_d
        y_unspecified += uns

        month_start = month_end
        year_start = year_end

        if at_year_end:
            #reset stats
            year_end = year_start + 1
            year_start=year_end
            month_start=1
            day_end= "-01"
            stats_str="{},{},{},{},{}".format(y_total, y_pdfs, y_xmls, y_unspecified, y_dl)
            yearly_stats[year_start]=stats_str

            at_year_end=False
            y_total=0
            y_pdfs=0
            y_xmls=0
            y_dl=0
            y_unspecified=0

        batch += 1

        if year_end >= end_year:
            break

    print("total={}, haspdf={}, hasxml={}, "
          "has unspecified={}, xmldownloaded={}".format(total, pdfs, xmls, unspecified, down))

    for k, v in yearly_stats.items():
        print("year={}, {}".format(k, v))
    f.close()
# with open('test_file.xml', 'wb+') as file:
#     link = requests.get('https://onlinelibrary.wiley.com/doi/full-xml/10.1002/asi.22643')
#     file.write(link.content)

