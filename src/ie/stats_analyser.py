import sys

from ie.eval import scorer
from ie.rule import feature_extractor as fe
from lxml import etree




if __name__ == "__main__":
    gazetteer_file="/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/taxonomy/taxonomy_ver7.xml"
    files = "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/new_data/JDOC/xml_parsed/full"
    gs_file="/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/jdoc_ZZ.csv"
    # files = "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/new_data/LISR/xml_parsed/full"
    # gs_file = "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/lisr_WT_AC.csv"

    parser = etree.XMLParser(recover=False)
    gazetteer_keyword, gazetteer_pattern = fe.load_gazetteer(gazetteer_file, parser)

    keep_files = scorer.load_files2keep(files)
    gs = scorer.read_gs(gs_file, 6, max_rows=653,
                 keepcls=None, keepfiles=keep_files)

    freq={}
    for k, v in gazetteer_keyword.items():
        freq[k]=0

    count=1
    for k, v in gs.items():
        annotations=v.split(",")
        print(str(count)+"="+v)
        count+=1

        for a in annotations:
            if a in freq.keys():
                freq[a]+=1
            else:
                print(a)

    methods=sorted(list(freq.keys()))
    for m in methods:
        print(m+","+str(freq[m]))



