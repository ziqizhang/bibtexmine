import csv

def read_gs(in_file, col, max_rows=None):
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
            annotations[row[0]]=row[col]

    return annotations

def read_prediction(in_file, col, take_all=False):
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
        multi_gs =gs_l.split(",")

        if match_all:
            gs_all += len(multi_gs)
        else:
            gs_all += 1

        if i not in pred.keys():
            continue

        pred_l=pred[i]
        multi_pred=pred_l.split(",")

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

    p=correct/pred_all
    r=correct / gs_all
    f1=2*p*r/(p+r)
    print("precision={}".format(p))
    print("recall={}".format(r))
    print("f1={}".format(f1))


if __name__ == "__main__":
    print("ZZ")
    #when multiple predictions, keep all; when multiple gs, keep all
    gs = read_gs("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/jdoc_ZZ.csv", 6, max_rows=508)
    pred=read_prediction("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/jdoc.csv",4,take_all=True)
    score(gs,pred,match_all=True)

    # when multiple predictions, keep the highest; when multiple gs, as long as one matches
    gs = read_gs("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/jdoc_ZZ.csv", 6, max_rows=508)
    pred = read_prediction("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/jdoc.csv", 4, take_all=False)
    score(gs, pred, match_all=False)

    print("AC")
    gs = read_gs("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/jdoc_AC.csv", 6, max_rows=348)
    pred = read_prediction("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/jdoc_.csv", 4,
                           take_all=True)
    score(gs, pred, match_all=True)

    # when multiple predictions, keep the highest; when multiple gs, as long as one matches
    gs = read_gs("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/jdoc_AC.csv", 6, max_rows=348)
    pred = read_prediction("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/jdoc_.csv", 4,
                           take_all=False)
    score(gs, pred, match_all=False)

    print("WT")
    # when multiple predictions, keep all; when multiple gs, keep all
    gs = read_gs("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/lisr_WT.csv", 7, max_rows=653)
    pred = read_prediction("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/lisr.csv", 4,
                           take_all=True)
    score(gs, pred, match_all=True)

    # when multiple predictions, keep the highest; when multiple gs, as long as one matches
    gs = read_gs("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/lisr_WT.csv", 7, max_rows=653)
    pred = read_prediction("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/extracted_feature/lisr.csv", 4,
                           take_all=False)
    score(gs, pred, match_all=False)

