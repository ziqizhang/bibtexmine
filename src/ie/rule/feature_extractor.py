# processes a parsed xml file and look for features as defined in the 'initial taxonomy' (ver 24 June)
import csv
import glob
import operator
import re
import xml.etree.cElementTree as ET

import sys
import os
from lxml import etree

MIN_WORDS_IN_FULL_TEXT=500

# load the gazetteer that contains keywords potentially mapping to concepts
def load_gazetteer(file, parser):
    keywords = {}
    patterns = {}
    xml = ET.parse(file, parser).getroot()
    concepts = xml.xpath("//concept")
    for c in concepts:
        cname = c.xpath("string(name)")

        keyword_elements = c.xpath("keywords/key")
        if keyword_elements is not None and len(keyword_elements) > 0:
            kwords = set()
            for ke in keyword_elements:
                kwords.add(ke.text)
            keywords[cname] = kwords

        regex_elements = c.xpath("regex/reg")
        if regex_elements is not None and len(regex_elements) > 0:
            ptns = {}
            for p in regex_elements:
                ptns[p.attrib["name"]] = (p.text)
            patterns[cname] = ptns

    return keywords, patterns


# check if an article has a method section
def find_method_section(parsed_xml_root_el, gazetteer_keywords: {} = None, gazetteer_patterns: {} = None):
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

    if method_section is not None:
        text = ""
        para = method_section.xpath("p")
        if para is None or len(para) == 0:
            text = re.sub('[^0-9a-zA-Z]+', ' ', method_section.text.lower())
            text = ' '.join(text.split())
        else:
            for p in para:
                p = re.sub('[^0-9a-zA-Z]+', ' ', p.text.lower())
                p = ' '.join(p.split())
                text += p + " "
        return text

    return None


def find_all_sections(parsed_xml_root_el, gazetteer_keywords: {} = None, gazetteer_patterns: {} = None,
                      methodseconly=False):
    k = "empirical study"
    if k not in gazetteer_keywords.keys() or len(gazetteer_keywords[k]) == 0:
        return False

    method_section_keywords = gazetteer_keywords[k]
    titles = ""
    secs = parsed_xml_root_el.xpath("sec")
    method_section = None
    for s in secs:
        if s.attrib is not None and "title" in s.attrib:
            title = s.attrib["title"].lower()
            titles += title + " "
            if has_keywords(method_section_keywords, title):
                method_section = s
                break

    text = ""

    if not methodseconly:
        for s in secs:
            para = s.xpath("p")
            for p in para:
                if p.text is None:
                    continue
                p = re.sub('[^0-9a-zA-Z]+', ' ', p.text.lower())
                p = ' '.join(p.split())
                text += p + " "
            if para == None or len(para) == 0:
                text = "".join(s.xpath("text()")).strip()
        return text, method_section is not None, titles.lower().strip()
    elif method_section is not None:
        para = method_section.xpath("p")
        for p in para:
            if p.text is None:
                continue
            p = re.sub('[^0-9a-zA-Z]+', ' ', p.text.lower())
            p = ' '.join(p.split())
            text += p + " "

        if para==None or len(para)==0:
            text = "".join(method_section.xpath("text()")).strip()
        return text, method_section is not None, titles.lower().strip()
    else:
        return text, method_section is not None, titles.lower().strip()


# find the section containing abstract from the Abstract parsed files
def find_abstract_section(parsed_xml_root_el):
    secs = parsed_xml_root_el.xpath("sec")
    if secs is not None and len(secs) == 1:
        return re.sub('[^0-9a-zA-Z]+', ' ', secs[0].text.lower())
    if secs is not None and len(secs) > 1:
        text = ""
        for sec in secs:
            p = re.sub('[^0-9a-zA-Z]+', ' ', sec.text.lower())
            p = ' '.join(p.split())
            text += p + " "

        return text
    return None

def find_doi(parsed_xml_root_el):
    secs = parsed_xml_root_el.xpath("doi")
    if secs is not None and len(secs) == 1:
        return secs[0].text.strip()

    return None


# count keyword frequencies in the 'method' section
def count_feature_freq(text, gazetteer_keywords: {} = None, gazetteer_patterns: {} = None):
    freq = {}

    if gazetteer_keywords is not None:
        # counting keyword frequencies
        for concept, kwords in gazetteer_keywords.items():
            if concept == "empirical study":
                continue
            sum = 0
            for k in kwords:
                found=re.finditer(r"\b"+k+r"\b", text)
                for f in found:
                    sum+=1
            freq[concept] = sum

    # apply regex
    if gazetteer_patterns is not None:
        for concept, patterns in gazetteer_patterns.items():
            if concept == "empirical study":
                continue
            for p_name, p_str in patterns.items():
                sum = len(re.findall(p_str, text))
                freq[concept + "-" + p_name] = sum

    return freq


def has_keywords(keywords, text):
    for k in keywords:
        if k in text:
            return True
    return False

def extract_features_non_zero_only(text, gazetteer_keywords: {} = None, gazetteer_patterns: {} = None):
    feature_freq = count_feature_freq(text,
                                      gazetteer_keywords=gazetteer_keywords,
                                      gazetteer_patterns=gazetteer_patterns)

    sorted_features = sorted(feature_freq.items(), key=operator.itemgetter(1), reverse=True)
    match_result = ""
    sum = 0
    for f in sorted_features:
        k = f[0]
        v = f[1]
        if v == 0:
            break
        else:
            match_result += k + "=" + str(v) + "|"
            sum += v

    if len(match_result)>0:
        return match_result.strip()[:len(match_result)-1], sum
    return match_result.strip(),sum


def string_to_features(match_string):
    values = []
    for f in match_string.split("|"):
        values.append(int(f.split("=")[1]))
    return values


def classify_abstract_by_feature(title_matches: str, abstract_matches: str, method_matches: str,
                                 full_matches: str, has_method=False):
    decision_index = -1
    if title_matches is not None and title_matches != "n/a" and len(title_matches) > 0:
        decision_matches = title_matches
        decision_index = 0
    elif abstract_matches is not None and abstract_matches != "n/a" and len(abstract_matches) > 0:
        decision_matches = abstract_matches
        decision_index = 1
    elif method_matches is not None and method_matches != "n/a" and len(method_matches) > 0:
        decision_matches = method_matches
        decision_index = 2
    else:
        return "Theory", decision_index

    row_of_features = string_to_features(decision_matches)
    nonzeros = 0
    for v in row_of_features:
        if int(v) > 0:
            nonzeros += 1

    '''
    more than one > empirical, (methodological is also theoretical)
    '''
    if not has_method:
        if nonzeros>1:
            return 'Empirical', decision_index
        return 'Theory', decision_index
    else:
        return 'Empirical',decision_index


def post_classify_refine(line_decision):
    if line_decision[4] == "n/a":
        line_decision[4] = "theory"
    if '|' in line_decision[4]:
        # when both ethnography and netnography exists, keep only netnography
        if 'netnography' in line_decision[4] and 'ethnography' in line_decision[4]:
            methods = line_decision[4].split("|")
            final_method = ""
            for m in methods:
                if 'ethnography' in m:
                    continue
                final_method+=m+"|"
            line_decision[4]=final_method

    return line_decision


def output_doi(doi, writer):
    if doi.startswith("http"):
        writer.write(doi+"\n")
    else:
        writer.write("https://doi.org/"+doi+"\n")


def extract_features(abstract_folder, full_text_folder, gazetter_file, outfile, file_ext):
    parser = etree.XMLParser(recover=False)
    # "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/taxonomy/taxonomy.xml"
    gazetteer_keyword, gazetteer_pattern = load_gazetteer(gazetter_file, parser)
    abstract_file_list = sorted(glob.glob(abstract_folder + '/*.*'))
    fulltext_file_list = sorted(glob.glob(full_text_folder + '/*.*'))
    titles = set()
    for abs in abstract_file_list:
        try:
            paper_title = abs.split("/")[-1]
            paper_title = paper_title[:paper_title.index(file_ext)]
            titles.add(paper_title)
        except ValueError:
            print("Not expected file:"+abs)
    for ft in fulltext_file_list:
        try:
            paper_title = ft.split("/")[-1]
            paper_title = paper_title[:paper_title.index(file_ext)]
            titles.add(paper_title)
        except ValueError:
            print("Not expected file:"+ft)
    titles = sorted(list(titles))

    header = ["Article", "hasMethodSection", "GeneralType", "ContentPart", "Features", "Sum", "Label", "Comment"]

    count = 0
    doi_writer=open("doi.txt",'w',newline="\n")

    with open(outfile, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for paper_title in titles:
            print("processing article=" + paper_title)

            #check length of article
            fulltext_file = full_text_folder + "/" + paper_title + file_ext
            if not os.path.isfile(fulltext_file):
                print("\t no body text, ignored")
                continue
            with open(fulltext_file, "r") as myfile:
                data = myfile.read()
                if len(data.split(" "))<MIN_WORDS_IN_FULL_TEXT:
                    print("\t very short article, ignored")
                    continue

            line_decision = [paper_title, "", "", "DECISION", "", ""]
            line_title = ["", "", "", "Title", "", ""]
            line_abs = ["", "", "", "Abstract", "", ""]
            line_method = ["", "", "", "Method_Section", "", ""]
            line_full = ["", "", "", "Full_Text(reference-only)", "", ""]

            # match title
            title_matches, title_matches_sum = extract_features_non_zero_only(paper_title.lower(),
                                                                              gazetteer_keywords=gazetteer_keyword,
                                                                              gazetteer_patterns=gazetteer_pattern)
            line_title[4] = title_matches
            line_title[5] = title_matches_sum

            doi=""
            # match abstract
            abstract_file = abstract_folder + "/" + paper_title + file_ext
            abstract_matches = None
            if os.path.isfile(abstract_file):
                tree = ET.parse(abstract_file, parser).getroot()
                target_section = find_abstract_section(tree)

                abstract_matches, abstract_matches_sum = extract_features_non_zero_only(target_section,
                                                                                        gazetteer_keywords=gazetteer_keyword,
                                                                                        gazetteer_patterns=gazetteer_pattern)
                line_abs[4] = abstract_matches
                line_abs[5] = abstract_matches_sum
                # extract doi from body text
                doi = find_doi(tree)
            else:
                line_abs[4] = "n/a"
                line_abs[5] = "0"


            # match full text
            method_matches = None
            has_method = False
            full_matches = None
            if os.path.isfile(fulltext_file):
                # method section
                tree = ET.parse(fulltext_file, parser).getroot()
                method_section, has_method, section_titles = find_all_sections(tree,
                                                                               gazetteer_keywords=gazetteer_keyword,
                                                                               methodseconly=True)
                if has_method:
                    line_method[1] = "True"
                    method_matches, method_matches_sum = extract_features_non_zero_only(method_section,
                                                                                        gazetteer_keywords=gazetteer_keyword,
                                                                                        gazetteer_patterns=gazetteer_pattern)
                    line_method[4] = method_matches
                    line_method[5] = method_matches_sum
                else:
                    line_method[4] = "n/a"
                    line_method[5] = "0"

                # full text
                fulltext, has_method, section_titles = find_all_sections(tree,
                                                                         gazetteer_keywords=gazetteer_keyword,
                                                                         methodseconly=False)
                full_matches, full_matches_sum = extract_features_non_zero_only(fulltext,
                                                                                gazetteer_keywords=gazetteer_keyword,
                                                                                gazetteer_patterns=gazetteer_pattern)
                line_full[4] = full_matches
                line_full[5] = full_matches_sum

                #extract doi from body text
                if doi is None or doi=="":
                    doi = find_doi(tree)

            output_doi(doi,doi_writer)
            # classify into theory, methodological, empirical, also decision which of title, abs, method, full text to use for decision

            general_type, decision_index = \
                classify_abstract_by_feature(title_matches, abstract_matches, method_matches,
                                             full_matches, has_method)

            if decision_index == -1:
                line_decision[4] = "n/a"
            elif decision_index == 0:
                line_decision[4] = line_title[4]
            elif decision_index == 1:
                line_decision[4] = line_abs[4]
            elif decision_index == 2:
                line_decision[4] = line_method[4]

            #refine classification results based on rules
            line_decision = \
                post_classify_refine(line_decision)

            line_decision[1]=has_method
            line_decision[2]=general_type
            writer.writerow(line_decision)
            writer.writerow(line_title)
            writer.writerow(line_abs)
            writer.writerow(line_method)
            writer.writerow(line_full)

        print("finished")
        doi_writer.close()

if __name__ == "__main__":

    # text="Algorithmic detection of misinformation and disinformation Gricean perspectives"
    # word="detection" #or passed by other functions etc.
    # found=re.finditer(r"\b"+word+r"\b", text)
    # for i in found:
    #     print("found")

    extract_features("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/JDOC/xml_parsed/abstract",
                     "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/JDOC/xml_parsed/full",
                     "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/taxonomy/taxonomy_ver7.xml",
                     "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/jdoc.csv",".xml.txt")

    extract_features("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/LISR/xml_parsed/abstract",
                     "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/LISR/xml_parsed/full",
                     "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/taxonomy/taxonomy_ver7.xml",
                     "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/lisr.csv",".xml.txt")
    #
    extract_features("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/JASIST_(issn_2330-1635)/jasist_html_parsed/abstract",
                     "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/JASIST_(issn_2330-1635)/jasist_html_parsed/full_text",
                     "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/taxonomy/taxonomy_ver7.xml",
                     "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/jasist.csv",".txt")
