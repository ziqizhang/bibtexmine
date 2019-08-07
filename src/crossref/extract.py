# File to extract data from a given XML file
import glob
import xml.etree.cElementTree as ET
from lxml import etree


# method to extract the abstract from a given index
# if not found at e.g. index 25, it will go to 24,23,22..1
def grab_abstract(index):
    grab = root[0][index].text
    if(grab.find("Abstract") >0):
        return grab
#         print("true")
    elif index ==1:
        return "No abstract found"
    else:
        index-=1
        grab_abstract(index)

parser = etree.XMLParser(recover=True)
# load the xml files
file_list = glob.glob('E:exported_data\\extracted_data\\LISR\\xml\\' + '*.xml')
count = 0
abs_count = 0
for f in file_list:
    try:
        # print(f)
        tree = etree.parse(f, parser=parser)
        root = tree.getroot()
        # print(root[0][6].text)
        file_name = f[:-4] + '.txt'
        grab = grab_abstract(26)
        if(len(grab)) > 30:
            with open((file_name), 'w+') as file:
                # print(i['link'][1]['URL'])
#                 print(len(grab))
                file.write(grab)
#                 print(grab)
    except:
#         print("error occured")
        count += 1
    finally:
        # print(count)
        # file.close()
        print("finished")

