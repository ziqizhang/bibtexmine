import glob
import xml.etree.cElementTree as ET
import sys
import os
from lxml import html
from xml.sax.saxutils import escape

def parse(in_file, xml_parser: ET.XMLParser):
    return ET.parse(in_file, parser=xml_parser)


file_list = glob.glob('E:exported_data\\' + '/*.html')
count = 0
for f in file_list:

    file_name = f[:-5]
    print("Processing... " + file_name)
    try:
        root = html.parse(f).getroot()
        element = root.get_element_by_id("section-1-en")
        abstract = element.text_content()
        doi = "\n<doi> " + root.find_class("epub-doi")[0].text_content() + "</doi>"
        count+=1
        # el = root.xpath("//div[@class='article__body']")
        # the id content
        # print (element.text_content())
        file_name = f[:-6] + '.txt'

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
        print('err at <> ' + file_name)

print('Extracted ', count, ' out of ', len(file_list))
