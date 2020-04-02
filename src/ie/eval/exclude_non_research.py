#exclude articles that are not research papers from the GS, and recreate another GS file
from ie.eval import scorer
import csv

def exclude_gs(gs_file, new_gs_file, keepfiles):
    annotations={}
    outf=open(new_gs_file, 'w', newline='')
    csvwriter = csv.writer(outf, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    with open(gs_file) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        count=0
        count_skip=0
        skip=None
        for row in csvreader:
            count += 1

            if count==1:
                csvwriter.writerow(row)
                continue

            if skip is None:
                if not row[0] in keepfiles:
                    skip=True
                    continue
                else:
                    csvwriter.writerow(row)
                    skip=False
                    continue

            if skip:
                count_skip+=1
                if count_skip==4:
                    skip=None
                    count_skip=0
            else:
                count_skip += 1
                csvwriter.writerow(row)
                if count_skip == 4:
                    skip = None
                    count_skip=0


    outf.close()
    return annotations

if __name__ == "__main__":
    # k_files = "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/new_data/JDOC/xml_parsed/full"
    # gs="/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/jdoc_ZZ.csv"
    # n_gs="/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/jdoc_ZZ_new.csv"

    k_files = "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_data/new_data/LISR/xml_parsed/full"
    gs = "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/lisr_WT_AC.csv"
    n_gs = "/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/lisr_WT_AC_new.csv"

    keep_files = scorer.load_files2keep(k_files)
    exclude_gs(gs, n_gs, keep_files)