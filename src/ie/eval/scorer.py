import csv

def read_gs(in_file, col, max_rows=None, keep=None):
    annotations={}
    with open(in_file) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        count=0
        for row in csvreader:
            if "An empirical study of the information seeking behavior of practicing visual artists" in [row[0]]:
                print()
            count += 1
            if max_rows is not None and count>max_rows:
                break

            if count==1:
                continue
            if len(row[0])==0:
                continue

            ann = row[col].strip()
            if keep is not None:
                ann=replace_with_other(ann, keep)
            annotations[row[0]]=ann

    return annotations


def replace_with_other(pred_, keep):
    values=pred_.split(",")
    replaced_values=set()
    for v in values:
        v=v.strip()
        if v in keep:
            replaced_values.add(v)
        else:
            replaced_values.add("other")
    string=""
    for v in replaced_values:
        string+=v+","
    return string[0:-1].strip()


def read_prediction(in_file, col, take_all=False,keep=None):
    predictions = {}
    with open(in_file) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        count = 0
        for row in csvreader:
            count += 1
            if count == 1:
                continue
            if len(row[0]) == 0:
                continue
            pred=row[col]

            pred_ = ""
            if take_all:
                for p in pred.split("|"):
                    pred_+=p.split("=")[0]+","
                pred_ = pred_[:-1]
            else:
                pred_=pred.split("|")[0].split("=")[0]

            if keep is not None:
                pred_ = replace_with_other(pred_, keep)
            predictions[row[0]] = pred_
    return predictions

#*args = filter labels
def score(gs:dict, pred:dict, match_all=False):
    instances=sorted(list(gs.keys()))

    gs_labels=[]
    pred_labels=[]

    #find correct annotations
    correct=0
    pred_all=0
    gs_all=0
    for i in instances:
        gs_l = gs[i]
        multi_gs =split_by_comma(gs_l)

        if match_all:
            gs_all += len(multi_gs)
        else:
            gs_all += 1

        if i not in pred.keys():
            continue

        pred_l=pred[i]
        multi_pred=split_by_comma(pred_l)

        # if len(multi_pred)>1:
        #     print("")
        if match_all:
            pred_all+=len(multi_pred)
        else:
            pred_all+=1

        shared=len(set(multi_gs).intersection(multi_pred))
        if shared==0:
            print("\t {}, gs={}, pred={}".format(i, gs_l, pred_l))
        if match_all:
            correct+=shared
        else:
            if shared>0:
                correct+=1

    if pred_all==0 or gs_all==0:
        p=0
        r=0
        f1=0
    else:
        p=correct/pred_all
        r=correct / gs_all
        f1=2*p*r/(p+r)
    # print("precision={}".format(p))
    # print("recall={}".format(r))
    # print("f1={}".format(f1))
    print(",{},{},{}".format(p, r, f1))


def find_all_classes(gs:dict):
    classes=set()
    for v in gs.values():
        multi_gs = split_by_comma(v)
        classes.update(multi_gs)

    return classes


def filter_(c, gs:dict):
    filtered={}
    for k, v in gs.items():
        multi_values = split_by_comma(v)
        if c in multi_values:
            filtered[k]=v
    return filtered


def score_per_type(gs:dict, pred:dict, match_all=False):
    #get the unique classes available
    unique_classes=find_all_classes(gs)

    #going through each class and calculate scores
    for c in unique_classes:
        print("CLASS={}".format(c), end='')
        filtered_gs=filter_(c, gs)
        filtered_pred=filter_(c, pred)
        score(filtered_gs, filtered_pred, match_all)


def split_by_comma(string):
    res=[]
    for s in string.split(","):
        res.append(s.strip())
    return res

if __name__ == "__main__":
    # print("ZZ")
    # #when multiple predictions, keep all; when multiple gs, keep all
    # gs = read_gs("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/jdoc_ZZ.csv", 6, max_rows=508)
    # pred=read_prediction("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/jdoc.csv",4,take_all=True)
    # score(gs,pred,match_all=True)
    #
    # # when multiple predictions, keep the highest; when multiple gs, as long as one matches
    # gs = read_gs("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/jdoc_ZZ.csv", 6, max_rows=508)
    # pred = read_prediction("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/jdoc.csv", 4, take_all=False)
    # score(gs, pred, match_all=False)

    # print("AC")
    # gs = read_gs("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/jdoc_AC.csv", 6, max_rows=348)
    # pred = read_prediction("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/jdoc_.csv", 4,
    #                        take_all=True)
    # score(gs, pred, match_all=True)
    #
    # # when multiple predictions, keep the highest; when multiple gs, as long as one matches
    # gs = read_gs("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/jdoc_AC.csv", 6, max_rows=348)
    # pred = read_prediction("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/jdoc_.csv", 4,
    #                        take_all=False)
    # score(gs, pred, match_all=False)
    keep=["questionnaire","interview","scientometric","theory"]

    print("jdoc")
    print(">>> match_all=True")
    #when multiple predictions, keep all; when multiple gs, keep all
    gs = read_gs("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/jdoc_ZZ.csv", 6, max_rows=508, keep=keep)
    pred=read_prediction("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/jdoc.csv",4,take_all=True, keep=keep)
    score_per_type(gs,pred,match_all=True)

    print(">>> match_all=False")
    # when multiple predictions, keep the highest; when multiple gs, as long as one matches
    gs = read_gs("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/jdoc_ZZ.csv", 6, max_rows=508, keep=keep)
    pred = read_prediction("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/jdoc.csv", 4, take_all=False, keep=keep)
    score_per_type(gs, pred, match_all=False)
    print()

    print("lisr")
    print(">>> match_all=True")
    # when multiple predictions, keep all; when multiple gs, keep all
    gs = read_gs("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/lisr_WT_AC.csv", 6, max_rows=653, keep=keep)
    pred = read_prediction("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/lisr.csv", 4,
                           take_all=True, keep=keep)
    #score(gs, pred, match_all=True)
    score_per_type(gs, pred, match_all=True)

    print(">>> match_all=False")
    # when multiple predictions, keep the highest; when multiple gs, as long as one matches
    gs = read_gs("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/lisr_WT_AC.csv", 6, max_rows=653, keep=keep)
    pred = read_prediction("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/lisr.csv", 4,
                           take_all=False, keep=keep)
    #score(gs, pred, match_all=False)
    score_per_type(gs, pred, match_all=False)

