'''
Reads a scopus dump of paper data, replace the 'abstract' column with method sections from that paper
'''
import re
import xml.etree.cElementTree as ET

import sys
import pandas as pd
from lxml import etree
import glob
import ie.rule.feature_extractor as fe
import csv

#read parsed xml data (JDOC, LISR or JASIST), map doi to file name
def map_parsed_xml(infolder):
    map={}

    parser = etree.XMLParser(recover=False)
    file_list = sorted(glob.glob(infolder + '/*.*'))

    for file in file_list:
        print(file)
        tree = ET.parse(file, parser).getroot()
        doi = tree.xpath("doi")
        doi=doi[0].text.strip()
        if doi.startswith("https://doi.org/"):
            doi=doi[16:]
        map[doi]=file

    return map


def has_keywords(keywords, text):
    for k in keywords:
        if k in text:
            return True
    return False

def find_method_section(parsed_xml_root_el, gazetteer_keywords: {} = None):
    k = "empirical study"
    if k not in gazetteer_keywords.keys() or len(gazetteer_keywords[k]) == 0:
        return False

    method_section_keywords = gazetteer_keywords[k]
    secs = parsed_xml_root_el.xpath("sec")
    method_section = None
    for s in secs:
        if s.attrib is not None and "title" in s.attrib:
            title = s.attrib["title"].lower()
            if has_keywords(method_section_keywords, title):
                method_section = s
                break

    if method_section is None:
        return None
    else:
        str=""
        for m in method_section:
            if m.text==None:
                continue
            str+=m.text+" "
        return str.strip()


if __name__ == "__main__":
    '''
/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/new_data/JDOC/xml_parsed/full
/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/scopus_data/original/jdoc_scopus.csv
/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/taxonomy/taxonomy_ver7.xml
/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/scopus_data/abstract_replaced/jdoc_method.csv
12
16

/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/new_data/JASIST/full
/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/scopus_data/original/jasist_2008_2014_all.csv
/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/taxonomy/taxonomy_ver7.xml
/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/scopus_data/abstract_replaced/jasist_method_2008_2014.csv
12
16

/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/new_data/JASIST/full
/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/scopus_data/original/jasist_2014_2018_all.csv
/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/taxonomy/taxonomy_ver7.xml
/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/scopus_data/abstract_replaced/jasist_method_2014_2018.csv
12
16

/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/new_data/LISR/xml_parsed/full
/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/scopus_data/original/lisr_scopus.csv
/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/taxonomy/taxonomy_ver7.xml
/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/scopus_data/abstract_replaced/lisr_method.csv
12
16
    '''

    #create the doi-file name map
    map=map_parsed_xml(sys.argv[1])

    #load scopus data dump
    scopus_data_file=sys.argv[2]
    df = pd.read_csv(scopus_data_file, header=0, delimiter=",", quotechar='"', encoding="utf-8")
    headers= list(df.columns.values)

    df.fillna('')
    df=df.as_matrix()

    #load gazetteer
    gazetteer_file=sys.argv[3]
    parser = etree.XMLParser(recover=False)
    gazetteer_keyword, gazetteer_pattern = fe.load_gazetteer(gazetteer_file, parser)

    #process and create new scopus data dump
    new_scopus_data_file=sys.argv[4]
    doi_col=int(sys.argv[5])
    abstract_col = int(sys.argv[6])

    count_has_method=0
    count_total=0
    with open(new_scopus_data_file, mode='w') as outfile:
        outfile_writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        outfile_writer.writerow(headers)
        for row in df:
            doi = row[doi_col]
            if doi not in map.keys():
                continue

            file = map[doi]
            #print("\t" + file)
            xml = ET.parse(file, parser).getroot()
            method=find_method_section(xml, gazetteer_keyword)
            count_total+=1
            if method==None:
                count_has_method+=1
                print("\t err: file has no method section - {}".format(file))
                method=""

            method_text=re.sub(r'\n\s+'," ", method).strip()
            row[abstract_col]=method_text
            outfile_writer.writerow(row)
    print(count_has_method)
    print(count_total)