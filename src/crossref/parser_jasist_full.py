import glob
import xml.etree.cElementTree as ET
import sys
import os
from lxml import html
from lxml.html import html_parser

# doc @https://lxml.de/lxmlhtml.html
types={}

def parse(in_file, xml_parser: ET.XMLParser):
    return ET.parse(in_file, parser=html_parser)

# full
file_list = glob.glob('/home/zz/Cloud/GDrive/ziqizhang/project/'
                      'sure2019/data/extracted_data/JASIST_(issn_2330-1635)/jasist_html_parsed/html/*.html')
out_folder='/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/JASIST_(issn_2330-1635)/tmp/'

count = 0
count_non_html=0
count_no_ful=0
count_other_error=0

for f in file_list:
    try:
        root = html.parse(f).getroot()
        if "application/pdf" in root.text_content().lower() or "Adobe LiveCycle PDF" in root.text_content():
            print('\terr: not html ')
            count_non_html += 1
            continue

        type=root.find_class("doi-access-container clearfix")[0].text_content()
        type=type.split("\n")[0].strip()
        if type in types:
            types[type] += 1
        else:
            types[type] = 1

        try:
            element = root.find_class("article-section article-section__full")
        except:
            print('\terr: NO FULL TEXT ')
            count_no_ful+=1
            continue

        doi = "\n<doi> " + root.find_class("epub-doi")[0].text_content() + "</doi>"
        full_text = element[0]
        file_name = out_folder + f.split("/")[-1] + ".xml"

        outf = ""
        for i in full_text[:-1]:
            # print ("line -> ", i)
            title = '\n<sec title=' + '"' + i[0].text_content() + '">\n'
            outf = outf + title
            for j in i[1:]:
                count = 0
                paragraph = ("\n<p>" + j.text_content().strip() + "</p>")
                outf += paragraph
        #         print("length = " , len("<p>" + j.text_content() + "</p>\n"))
        with open((file_name), 'wb+') as file:
            # print(i['link'][1]['URL'])
            #                 print(len(grab))
            file.write(("<doc>" +
                         doi +
                         "\n" + outf + \
                        "</doc>").encode("utf-8"))
            print("passed")

    except:
        print('\terr at <> ')
        count_other_error += 1

print(types)
print('Not html {}, no abstract {}, other error {}'.format(count_non_html, count_no_ful, count_other_error))