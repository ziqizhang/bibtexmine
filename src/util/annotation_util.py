
import csv

#check % of incorrect, correct
def check(inCSV, endline=None):
    with open(inCSV, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')

        count={}
        correct={}
        rows=0
        for row in csvreader:
            if rows==0:
                rows+=1
                continue

            if endline is not None and rows>endline:
                break

            rows+=1
            type=row[2]
            ann = row[26].lower()

            if type in count.keys():
                count[type]+=1
            else:
                count[type]=1

            if 'incorrect' in ann:
                continue
            else:
                if type in correct.keys():
                    correct[type]+=1
                else:
                    correct[type]=1

        for k, v in count.items():
            c=correct[k]
            print(k+"="+str(v)+", correct="+str(c)+", as percentage="+str(c/v))

if __name__ == "__main__":
    check("/home/zz/Cloud/GDrive/ziqizhang/project/sure2019/data/lisr_abstract_check.csv",endline=54)