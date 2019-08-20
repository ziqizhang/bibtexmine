# File to extract data from a given XML file
import glob
import xml.etree.cElementTree as ET

import sys

import os
from lxml import etree
from xml.sax.saxutils import escape


def parse(in_file, xml_parser: ET.XMLParser):
    return ET.parse(in_file, parser=xml_parser).getroot()
    #pass

def extract_doi(xml):
    doi=xml.xpath("string(//article-meta/article-id[@pub-id-type='doi'])")
    return doi

def extract_abstract(xml, outfolder, filename):
    doi=extract_doi(xml)
    abs_secs=xml.xpath("//front/article-meta/abstract/sec")
    if abs_secs is not None and len(abs_secs)>0:
        outfilename = outfolder + "/abstract/" + filename
        if not os.path.exists(os.path.dirname(outfilename)):
            os.makedirs(os.path.dirname(outfilename))

        with open(outfilename, 'w',encoding="utf-8") as outf:
            outf.write("<doc>")
            outf.write("<doi>"+doi+"</doi>\n")
            #outf.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            #for each section
            for i in range(1, len(abs_secs)+1):
                #section title
                title = xml.xpath('string(//front/article-meta/abstract/sec['+str(i)+']/title)').strip()
                if title is not None and len(title)>0:
                    out_string='<sec title="'+escape(title)+'">\n'
                else:
                    out_string="<sec>\n"

                #section content
                sec_para = xml.xpath("//front/article-meta/abstract/sec["+str(i)+"]/p")
                if(len(sec_para)==0):
                    continue
                for j in range(1, len(sec_para) + 1):
                    text=xml.xpath('string(//front/article-meta/abstract/sec['+str(i)+']/p['+str(j)+'])').strip()
                    out_string+=escape(text)+"\n"

                outf.write(out_string)
                outf.write("</sec>\n")

            outf.write("</doc>")
            outf.close()



def extract_fulltext(xml, outfolder, filename):
    doi = extract_doi(xml)
    body_secs = xml.xpath("//body/sec")
    if body_secs is not None and len(body_secs) > 0:
        outfilename = outfolder + "/full/" + filename
        if not os.path.exists(os.path.dirname(outfilename)):
            os.makedirs(os.path.dirname(outfilename))

        with open(outfilename, 'w', encoding="utf-8") as outf:
            outf.write("<doc>")
            outf.write("<doi>" + doi + "</doi>\n")
            # outf.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            # for each section
            for i in range(1, len(body_secs) + 1):
                # section title
                title = xml.xpath('string(//body/sec[' + str(i) + ']/title)').strip()
                if title is not None and len(title) > 0:
                    out_string='<sec title="' + escape(title) + '">\n'
                else:
                    out_string="<sec>\n"

                outf.write(out_string)
                # section content
                sec_para = xml.xpath("//body/sec[" + str(i) + "]//text()")
                if len(sec_para)<1:
                    continue
                text = "".join(sec_para).strip()
                # for j in range(1, len(sec_para) + 1):
                #     text = xml.xpath(
                #         'string(//body/sec[' + str(i) + ']/p[' + str(j) + '])').strip()
                #     if len(text)>1:
                #         text="<p>"+escape(text)+"</p>\n"
                #     out_string+=text

                outf.write(escape(text))
                outf.write("</sec>\n")
            outf.write("</doc>")
            outf.close()


if __name__ == "__main__":
    parser = etree.XMLParser(recover=True)
    file_list = sorted(glob.glob(sys.argv[1]+'/*.xml'))
    out_folder = sys.argv[2]
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
        print("\textracting abstract...")
        extract_abstract(tree, out_folder, filename)
        print("\textracting full text...")
        extract_fulltext(tree, out_folder,filename)


        #
        print("finished")
