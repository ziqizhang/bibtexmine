import glob
import xml.etree.cElementTree as ET
import sys
import os
from lxml import html
from lxml.html import html_parser

# doc @https://lxml.de/lxmlhtml.html

def parse(in_file, xml_parser: ET.XMLParser):
    return ET.parse(in_file, parser=html_parser)

# full
file_list = glob.glob('E:exported_data\\' + '/*.html')
file = file_list

for f in file_list:
    try:
        root = html.parse(f).getroot()
        element = root.find_class("article-section article-section__full")
        doi = "\n<doi> " + root.find_class("epub-doi")[0].text_content() + "</doi>"
        full_text = element[0]
        file_name = f[:-6] + '.txt'
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
        print("err <>")