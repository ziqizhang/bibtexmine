# File to extract data from a given XML file
import glob
import xml.etree.cElementTree as ET

import sys

import os
from lxml import etree
from xml.sax.saxutils import escape

types={}
dois=[]

def save_doi(outfile, dois):
    with open(outfile, 'w', encoding="utf-8") as outf:
        for d in dois:
            outf.write("https://doi.org/"+d+"\n")

def parse(in_file, xml_parser: ET.XMLParser):
    return ET.parse(in_file, parser=xml_parser).getroot()
    #pass

def check_article_type(xml):
    type=xml.xpath("string(//article-meta/article-categories/subj-group/subj-group[@subj-group-type='type-of-article'])")
    type=type.strip()
    if len(type)==0:
        type = xml.xpath(
            "string(//compound-subject-part[@content-type='label'])")
        type = type.strip()

    print("\tarticle type="+type)
    if type in types:
        types[type]+=1
    else:
        types[type]=1

    return type.lower()=="research paper" or type.lower()=="case study"

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
    else:
        abs_text = xml.xpath("string(//front/article-meta/abstract)")
        if len(abs_text)>0:
            outfilename = outfolder + "/abstract/" + filename
            with open(outfilename, 'w',encoding="utf-8") as outf:
                outf.write("<doc>")
                outf.write("<doi>"+doi+"</doi>\n")
                #outf.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                #for each section
                out_string="<sec>\n"
                out_string+=escape(abs_text)+"\n"
                outf.write(out_string)
                outf.write("</sec>\n")
                outf.write("</doc>")
                outf.close()
        else:
            print("\tNO ABSTRACT")


def extract_fulltext(xml, outfolder, filename):
    doi = extract_doi(xml)
    body_secs = xml.xpath("//body/sec")
    if body_secs is not None and len(body_secs) > 0:
        outfilename = outfolder + "/full/" + filename
        if not os.path.exists(os.path.dirname(outfilename)):
            os.makedirs(os.path.dirname(outfilename))

        dois.append(doi)

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
        filename = f.split("/")[-1].strip() + '.txt'

        if 'model of uncertainty ' in filename:
            print()
        print("processing file="+f)
        # try:
        # print(f)
        count += 1
        tree = parse(f, parser)
        # print(root[0][6].text)
        is_article = check_article_type(tree)
        if not is_article:
            print("\tthis is not a research article, skipped")
            continue


        print("\textracting abstract...")
        extract_abstract(tree, out_folder, filename)
        print("\textracting full text...")
        extract_fulltext(tree, out_folder,filename)


        #
        print("finished")

    print(types)
    save_doi(sys.argv[3], dois)