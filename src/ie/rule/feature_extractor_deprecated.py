# processes a parsed xml file and look for features as defined in the 'initial taxonomy' (ver 24 June)
import csv
import glob
import re
import xml.etree.cElementTree as ET

import sys
import os
from lxml import etree


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


def find_all_sections(parsed_xml_root_el, gazetteer_keywords: {} = None, gazetteer_patterns: {} = None):
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
    for s in secs:
        para = s.xpath("p")
        for p in para:
            if p.text is None:
                continue
            p = re.sub('[^0-9a-zA-Z]+', ' ', p.text.lower())
            p = ' '.join(p.split())
            text += p + " "
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
                f = text.count(k)
                sum += f
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


def create_feature_list(gazetteer_keyword: {}, gazetteer_patterns: {} = None):
    names = list(gazetteer_keyword.keys())
    names.remove("empirical study")

    if gazetteer_pattern is not None:
        for concept, patterns in gazetteer_patterns.items():
            for p_name, p_str in patterns.items():
                names.append(concept + "-" + p_name)

    names = sorted(names)
    names.insert(0, "empirical_study")
    return names


def extract_features(text, row: list, feature_list: list, fl_start_index: int, gazetteer_keywords: {} = None,
                     gazetteer_patterns: {} = None):
    feature_freq = count_feature_freq(text,
                                      gazetteer_keywords=gazetteer_keywords,
                                      gazetteer_patterns=gazetteer_patterns)
    sum = 0
    for i in range(fl_start_index, len(feature_list)):
        feature_name = feature_list[i]
        if feature_name in feature_freq.keys():
            feature_value = feature_freq[feature_name]
            row.append(feature_value)
            sum += feature_value
        else:
            row.append("")
    row.append(sum)
    return row


def extract_features_non_zero_only(text, gazetteer_keywords: {} = None, gazetteer_patterns: {} = None):
    feature_freq = count_feature_freq(text,
                                      gazetteer_keywords=gazetteer_keywords,
                                      gazetteer_patterns=gazetteer_patterns)
    match_result = ""
    for i in range(2, len(feature_list)):
        feature_name = feature_list[i]
        if feature_name in feature_freq.keys():
            feature_value = feature_freq[feature_name]
            if feature_value > 0:
                match_result += feature_name + "=" + str(feature_value) + "|"
    return match_result


def classify_abstract_by_feature(row_of_features):
    nonzeros = 0
    for v in row_of_features:
        if type(v) is str:
            continue
        if int(v) > 0:
            nonzeros += 1

    if nonzeros == 0:
        return 'Theory'
    elif nonzeros == 2 or nonzeros == 3:
        return 'Mixed_Method'
    elif nonzeros > 4:
        return 'Methodological'
    elif nonzeros == 1:
        return 'Empirical'
    else:
        return '?'


if __name__ == "__main__":

    '''
    jdoc:
    /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/JDOC/xml_parsed/full /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/taxonomy/taxonomy_ver3.xml /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/jdoc_full.csv full
    full

    /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/JDOC/xml_parsed/abstract /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/taxonomy/taxonomy_ver3.xml /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/jdoc_abstract.csv abs
    abs

    lisr:
    /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/LISR/xml_parsed/full /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/taxonomy/taxonomy_ver3.xml /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/lisr_full.csv full
    full

    /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/LISR/xml_parsed/abstract /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/taxonomy/taxonomy_ver3.xml /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/lisr_abstract.csv abs
    abs

    jaist:
    /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/JASIST_(issn_2330-1635)/jasist_html_parsed/full_text /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/taxonomy/taxonomy_ver3.xml /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/jaist_full.csv full
    full

    /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/JASIST_(issn_2330-1635)/jasist_html_parsed/abstract /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/taxonomy/taxonomy_ver3.xml /home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/jaist_abstract.csv abs
    abs
    '''

    parser = etree.XMLParser(recover=False)
    # "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/taxonomy/taxonomy.xml"
    gazetteer_keyword, gazetteer_pattern = load_gazetteer(sys.argv[2], parser)
    file_list = sorted(glob.glob(sys.argv[1] + '/*.*'))

    feature_list = create_feature_list(gazetteer_keyword, gazetteer_pattern)
    feature_list.extend(["Label", "Comment"])
    outfile = sys.argv[3]

    count = 0
    with open(outfile, 'w', newline='') as f:
        writer = csv.writer(f)
        feature_list.insert(0, "")
        feature_list.insert(1, "TITLE_MATCHES")  # matching keywords against paper title
        if sys.argv[4] == 'full':
            feature_list.insert(2, "SEC_TITLE_MATCHES")  # match keywords against section titles
        writer.writerow(feature_list)

        for f in file_list:
            print("processing file " + f)
            paper_title = filename = f.split("/")[-1].lower()
            title_matches = extract_features_non_zero_only(paper_title, gazetteer_keywords=gazetteer_keyword,
                                                           gazetteer_patterns=gazetteer_pattern)
            filename = paper_title + '.txt'
            row = [filename, title_matches]
            # try:
            # print(f)
            count += 1
            tree = ET.parse(f, parser).getroot()
            # print(root[0][6].text)

            # if sys.argv[4] == "full":
            #     target_section = find_method_section(tree, gazetteer_keywords=gazetteer_keyword)
            #     if target_section is not None:
            #         row.append("True")
            #     else:
            #         row.append("False")
            # else:
            #     row.append("unknown")
            #     target_section = find_abstract_section(tree)
            # if target_section is not None:
            #     extract_features(target_section, row, gazetteer_keywords=gazetteer_keyword,
            #                  gazetteer_patterns=gazetteer_pattern)
            # else:
            #     for i in range(2, len(feature_list)):
            #         row.append("0")
            # writer.writerow(row)
            if sys.argv[4] == "full":
                # target_section = find_method_section(tree, gazetteer_keywords=gazetteer_keyword)

                target_section, has_method, section_titles = find_all_sections(tree,
                                                                               gazetteer_keywords=gazetteer_keyword)
                sec_title_matches = extract_features_non_zero_only(section_titles, gazetteer_keywords=gazetteer_keyword,
                                                                   gazetteer_patterns=gazetteer_pattern)
                row.append(sec_title_matches)
                if has_method:
                    row.append("True")
                else:
                    row.append("False")

                if target_section is not None:
                    extract_features(target_section, row, feature_list=feature_list,
                                     fl_start_index=4,
                                     gazetteer_keywords=gazetteer_keyword,
                                     gazetteer_patterns=gazetteer_pattern)
                else:
                    for i in range(2, len(feature_list)):
                        row.append("0")
            else:
                target_section = find_abstract_section(tree)

                extract_features(target_section, row, feature_list=feature_list,
                                 fl_start_index=3,
                                 gazetteer_keywords=gazetteer_keyword,
                                 gazetteer_patterns=gazetteer_pattern)
                label = classify_abstract_by_feature(row)
                row.insert(1, label)

            writer.writerow(row)

            print("finished")
