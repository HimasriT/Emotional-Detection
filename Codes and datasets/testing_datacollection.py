from data_collection import by_user,init_api
from threading import Thread
import gc
import json
file_name = './DB2/users_list.txt'
db_loc = './DB2/raw_data/'
users_list = open(file_name)
users = dict()
threads = list()
for line in users_list:
    cur = 0
    user = line[:-1] if str(line).endswith('\n') else line
    print(user)
    threads.append(Thread(target=by_user,args=(user,init_api(),'904278686517452800','988852393977999360',db_loc)))
    threads[-1].start()
    # break
for thread in threads:
    thread.join()
#project_envi\Scripts\python.exe testing_datacollection.py > op.txt
