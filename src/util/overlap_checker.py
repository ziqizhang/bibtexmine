#checks parsed xml articles and those obtainable by the scopus api to see how much overlap between them (based on doi match)
import csv
import glob
import xml.etree.cElementTree as ET

import sys
from lxml import etree

from crossref.parser import parser_generic


def load_dois_scopus(file, col):
    dois=set()
    with open(file, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        cr=0
        for row in reader:
            cr+=1
            if cr==1:
                continue
            doi=row[col].lower()
            dois.add(doi)
    return sorted(list(dois))

def load_dois_crossref_xml(folder):
    parser = etree.XMLParser(recover=False)
    file_list = sorted(glob.glob(folder + '/*.*'))
    #    out_folder = sys.argv[2]
    # print(file_list)
    count = 0
    dois=set()
    for f in file_list:
        #print("processing file " + f)
        # try:
        # print(f)
        count += 1
        tree = ET.parse(f, parser)
        # print(root[0][6].text)
        doi=parser_generic.get_doi(tree.getroot())
        if doi is not None:
            dois.add(doi)
        #
       # print("finished")
    return sorted(list(dois))



if __name__ == "__main__":

    scopus_jdoc_dois = load_dois_scopus(
        "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/scopus_schema_and_data/jdoc_2018.csv", 12)
    crossref_jdoc_dois_full = load_dois_crossref_xml(
        "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/JDOC/xml_parsed/full")
    intersect = set(crossref_jdoc_dois_full).intersection(set(scopus_jdoc_dois))
    print("In crossref JDOC full:"+str(len(crossref_jdoc_dois_full)))
    print("In scopus JDOC full:" + str(len(scopus_jdoc_dois)))
    print("In both:"+str(len(intersect)))
    print("\n")


    crossref_jdoc_dois_abstract = load_dois_crossref_xml(
        "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/JDOC/xml_parsed/abstract")
    intersect = set(crossref_jdoc_dois_abstract).intersection(set(scopus_jdoc_dois))
    print("In crossref JDOC abstract:" + str(len(crossref_jdoc_dois_abstract)))
    print("In scopus JDOC abstract:" + str(len(scopus_jdoc_dois)))
    print("In both:" + str(len(intersect)))
    print("\n")


    scopus_lisr_dois=load_dois_scopus("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/scopus_schema_and_data/lisr.csv", 12)
    crossref_lisr_dois_full = load_dois_crossref_xml(
        "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/LISR/xml_parsed/full")
    intersect = set(crossref_lisr_dois_full).intersection(set(scopus_lisr_dois))
    print("In crossref LISR full:" + str(len(crossref_lisr_dois_full)))
    print("In scopus LISR full:" + str(len(scopus_lisr_dois)))
    print("In both:" + str(len(intersect)))
    print("\n")

    scopus_lisr_dois = load_dois_scopus(
        "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/scopus_schema_and_data/lisr.csv", 12)
    crossref_lisr_dois_abstract = load_dois_crossref_xml(
        "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/LISR/xml_parsed/abstract")
    intersect = set(crossref_lisr_dois_abstract).intersection(set(scopus_lisr_dois))
    print("In crossref LISR abstract:" + str(len(crossref_lisr_dois_abstract)))
    print("In scopus LISR abstract:" + str(len(scopus_lisr_dois)))
    print("In both:" + str(len(intersect)))
    print("\n")

    print("jdoc="+str(crossref_jdoc_dois_full))
    print("lisr=" + str(crossref_lisr_dois_full))
