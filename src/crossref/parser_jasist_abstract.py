import glob
import xml.etree.cElementTree as ET
import sys
import os
from lxml import html
from xml.sax.saxutils import escape

types={}

def parse(in_file, xml_parser: ET.XMLParser):
    return ET.parse(in_file, parser=xml_parser)

def check_article_type(type):
    return type.lower()=='research article'

file_list = glob.glob('/home/zz/Cloud/GDrive/ziqizhang/project/'
                      'sure2019/data/extracted_data/new_data/JASIST/html/*.txt')
out_folder='/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/new_data/JASIST/abstract/'

count = 0
count_non_html=0
count_no_abstract=0
count_other_error=0
for f in file_list:

    file_name = f[:-5]
    print("Processing... " + file_name)
    try:
        root = html.parse(f).getroot()
        if "application/pdf" in root.text_content().lower() or "Adobe LiveCycle PDF" in root.text_content():
            print('\terr: not html ')
            count_non_html += 1
            continue

        type=root.find_class("doi-access-container clearfix")[0].text_content().lower()
        type=type.split("\n")[0].strip()
        if type in types:
            types[type] += 1
        else:
            types[type] = 1
        if not check_article_type(type):
            continue

        try:
            element = root.get_element_by_id("section-1-en")
        except:
            print('\terr: NO ABSTRACT ')
            count_no_abstract+=1
            continue

        abstract = escape(element.text_content().strip())
        doi = "\n<doi> " + root.find_class("epub-doi")[0].text_content() + "</doi>"
        count+=1
        # el = root.xpath("//div[@class='article__body']")
        # the id content
        # print (element.text_content())
        title=f.split("/")[-1]
        try:
            title=root.findall("./head/meta[@name='citation_title']")[0].get('content')
        except:
            print("\tcannot parse title of the paper")
        file_name = out_folder+title.replace("/","_").strip() + ".xml"

        # print(element.text_content())
        with open((file_name), 'wb+') as file:
            # print(i['link'][1]['URL'])
            outf = "<doc>"+ \
                   doi + \
                   "\n<sec>" + abstract + \
                   "\n</sec>" + \
                   "\n</doc>"
            file.write(outf.encode("utf-8"))
            print("passed")
    except:
        print('\terr at <> ' + file_name)
        count_other_error+=1

print('Extracted ', count, ' out of ', len(file_list))
print(types)
print('Not html {}, no abstract {}, other error {}'.format(count_non_html, count_no_abstract, count_other_error))