from lxml import etree
import sys
import glob
import xml.etree.cElementTree as ET


def extract_doi(xml_tree):
    pass

def parse(in_file, xml_parser: ET.XMLParser):
    return ET.parse(in_file, parser=xml_parser).getroot()
    #pass

if __name__ == "__main__":
    parser = etree.XMLParser(recover=True)
    file_list = sorted(glob.glob(sys.argv[1]+'/*.xml'))
    out_file = sys.argv[2]
    # print(file_list)
    count = 0
    for f in file_list:
        filename = f.split("/")[-1] + '.txt'

        if 'model of uncertainty ' in filename:
            print()
        print("processing file "+f)
        # try:
        # print(f)
        count += 1
        tree = parse(f, parser)
        # print(root[0][6].text)
        print("\textracting doi...")
        doi=extract_doi(tree)

