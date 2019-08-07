#this parses the output xml files produced by parser_jodc/lisr

import glob
import xml.etree.cElementTree as ET

import sys

import os
from lxml import etree


def get_doi(xml):
    doi = xml.xpath("string(//doi)")
    if doi is None or len(doi)==0:
        return None
    return doi.lower()


def get_sections(xml):
    secs = xml.xpath("//sec")

    pass

if __name__ == "__main__":
    parser = etree.XMLParser(recover=False)
    file_list = sorted(glob.glob(sys.argv[1]+'/*.*'))
#    out_folder = sys.argv[2]
    # print(file_list)
    count = 0
    for f in file_list:
        print("processing file "+f)
        # try:
        # print(f)
        count += 1
        tree = ET.parse(f, parser)
        # print(root[0][6].text)
        get_doi(tree.getroot())


        #
        print("finished")