# File to extract data from a given XML file
import glob
import re
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

def check_article_type(xml, namespaces:dict):
    type=xml.xpath("string(//xocs:meta/xocs:document-type)", namespaces=namespaces)
    subtype=xml.xpath("string(//xocs:meta/xocs:document-subtype)", namespaces=namespaces)
    if type is None or len(type)==0:
        try:
            type=xml.xpath("//article[@article-type]")[0].attrib['article-type']
        except:
            type=""
    if type is None or len(type)==0:
        return False
    else:
        print("\tarticle type="+subtype)
        if subtype is None or len(subtype)==0:
            subtype=type

        if subtype in types:
            types[subtype] += 1
        else:
            types[subtype] = 1

        if type.lower()=="article" and subtype.lower()=="fla":
            return True
        if type.lower()=="research-article":
            return True
        return False

def extract_doi(xml,namespaces:dict):
    doi=xml.xpath("string(//dtd:coredata/prism:doi)",namespaces=namespaces)
    if len(doi)==0:
        doi=xml.xpath("string(//article/front/article-meta/article-id[@pub-id-type='doi'])")
    return doi

def extract_abstract(xml, outfolder, filename, namespaces:dict):
    doi=extract_doi(xml,namespaces=namespaces)
    abstract=xml.xpath("string(//dtd:coredata/dc:description)",namespaces=namespaces)
    if abstract is None or len(abstract) ==0:
        abstract = xml.xpath("string(//ce:abstract)", namespaces=namespaces)
    if abstract is None or len(abstract)==0:
        abstract = xml.xpath("string(//article/front/article-meta/abstract)")

    if abstract is not None and len(abstract)>0:
        outfilename = outfolder + "/abstract/" + filename
        if not os.path.exists(os.path.dirname(outfilename)):
            os.makedirs(os.path.dirname(outfilename))

        with open(outfilename, 'w',encoding="utf-8") as outf:
            outf.write("<doc>")
            outf.write("<doi>"+doi+"</doi>\n")
            #outf.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            #for each section
            abs=re.sub(r"\n\s+", " ", escape(abstract.strip()))
            outf.write("<sec>\n"+abs+"</sec>\n")
            outf.write("</doc>")
            outf.close()
    else:
        print("\tNO ABSTRACT")

def extract_para_of_section(sec):
    out_string=""
    para = sec.xpath("*[local-name()='para']")

    for j in range(0, len(para)):
        text = ''.join(para[j].itertext()).strip()
        if len(text) > 1:
            text = "<p>" + escape(text) + "</p>\n"
        out_string += text

    subsecs=sec.xpath("*[local-name()='section']")
    for s in subsecs:
        out_string+= extract_para_of_section(s)
    return out_string

def extract_fulltext(xml, outfolder, filename,namespaces:dict):
    doi = extract_doi(xml,namespaces=namespaces)

    #the 'article' element uses a namespace that overwrites default, we have to deal with it separately.
    original_text_article_element=xml.xpath('//*[local-name() = "article"]')
    if len(original_text_article_element)>0:
        dois.append(doi)
        body_secs = original_text_article_element[0].xpath("//*[local-name()='body']/*[local-name()='sections']")
        if body_secs is not None and len(body_secs)>0 and len(body_secs[0]) > 0:
            outfilename = outfolder + "/full/" + filename
            if not os.path.exists(os.path.dirname(outfilename)):
                os.makedirs(os.path.dirname(outfilename))

            with open(outfilename, 'w', encoding="utf-8") as outf:
                body_secs=body_secs[0]
                outf.write("<doc>")
                outf.write("<doi>" + doi + "</doi>\n")
                # outf.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                # for each section
                for i in range(0, len(body_secs)):
                    sec=body_secs[i]
                    # section title
                    title = escape(sec.xpath('string(ce:section-title)',namespaces=namespaces).strip())
                    if title is not None and len(title) > 0:
                        out_string='<sec title="' + title + '">\n'
                    else:
                        out_string="<sec>\n"

                    # section content
                    out_string+=extract_para_of_section(sec)

                    outf.write(out_string)
                    outf.write("</sec>\n")

                outf.write("</doc>")
                outf.close()
        else:
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
                            out_string = '<sec title="' + escape(title) + '">\n'
                        else:
                            out_string = "<sec>\n"

                        outf.write(out_string)
                        # section content
                        sec_para = xml.xpath("//body/sec[" + str(i) + "]//text()")
                        if len(sec_para) < 1:
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
    namespaces={'dtd':'http://www.elsevier.com/xml/svapi/article/dtd',
                'dc':'http://purl.org/dc/elements/1.1/',
                'ce':'http://www.elsevier.com/xml/common/dtd',
                'prism':'http://prismstandard.org/namespaces/basic/2.0/',
                'xocs':'http://www.elsevier.com/xml/xocs/dtd'}
    failed=set()
    count_research_articles=0
    for f in file_list:
        if "information seeking of coll" in f.lower():
            print("stop")
        try:
            filename = f.split("/")[-1].strip() + '.txt'
            print("processing file="+filename)
            # try:
            # print(f)
            count += 1
            tree = parse(f, parser)
            # print(root[0][6].text)
            is_article=check_article_type(tree, namespaces)
            if not is_article:
                print("\tthis is not a research article, skipped")
                continue
            count_research_articles+=1
            print("\textracting abstract...")
            extract_abstract(tree, out_folder, filename, namespaces)

            print("\textracting full text...")
            extract_fulltext(tree, out_folder,filename, namespaces)
        except AttributeError:
            failed.add(f)


        #
    print("finished, but the following files are failed:\n")
    print(count_research_articles)
    for f in failed:
        print(f)

    print(types)

    save_doi(sys.argv[3], dois)