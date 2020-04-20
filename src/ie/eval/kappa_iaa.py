import pandas as pd
from sklearn.metrics import cohen_kappa_score

#infile="/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/lisr_IAA_annotationcolumns.csv"
infile="/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/goldstandard/jdoc_IAA_annotationcolumns.csv"

df = pd.read_csv(infile, header=-1,delimiter=",", quotechar='"', encoding="utf-8").as_matrix()
arr1=[]
arr2=[]
for r in df:
    if type(r[0]) is float:
        continue
    arr1.append(r[0])
#    if r[1]=='theorys':
#        r[1]='theory'
    arr2.append(r[1])

print(cohen_kappa_score(arr1, arr2))

'''
LISR: 0.9118129614438064 (if 'conceptual analysis' (noted as 'theorys') from WT is retained then 0.7934347477982386
JDOC: 0.821278972354091

'''