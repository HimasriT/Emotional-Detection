import re
import json
REGEX_FILE = "./utils/regex_list.json"
class word_counter:
    def __init__(self,regex_dict=REGEX_FILE):
        self.regex_list = dict()
        if type(regex_dict) == type(str()):
            regex_dict = json.load(open(regex_dict))
        elif type(regex_dict) == type(dict()):
            pass
        else:
            print('invalid arg-regex_dict')
        for key in regex_dict:
            self.regex_list[key]=re.compile(regex_dict[key])
        print('regexs loaded')
    def word_count(self, text, cat_list=None):
        text = ' '+text.lower()+' '
        # print(text)
        res = list()
        if cat_list is None:
            cat_list= self.regex_list.keys()
        for key in cat_list:
            res.append(len(self.regex_list[key].findall(text)))
        return list(res),list(cat_list)
