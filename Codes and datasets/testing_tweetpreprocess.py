import csv
import gc
import json
import os
import re
from threading import Lock, Thread

from tweet_preprocess import (behave_features, ling_features_from_tweet,
                              satnxn_features, tweet_stats,
                              vis_features_from_tweet)

TWEETS_BATCH_SIZE = 200
NO_OF_THREADS = 4
NO_OF_JOBS_PER_THREAD = 40
gc.enable()
def thread_fun(db_loc,users,save_to_dir):
    for user in users:
        tdb = db_loc+'/'+user
        save_to = save_to_dir+'/'+user+'.csv'
        print(tdb,'started!!')
        tweets_list = os.listdir(tdb+'/tweets')
        file = open(save_to,'w',newline='',encoding='utf-8');pen = csv.writer(file)
        columns = False;data = list()
        counter = TWEETS_BATCH_SIZE
        for key in tweets_list:
            print(key)
            try:
                tweet = json.load(open(tdb+'/tweets/'+str(key)))
            except Exception:
                print("Error in reading:"+tdb+'/tweets/'+str(key))
                continue
            dat = list();cols = list()
            try:
                tdata, tcolumns = tweet_stats(tweet)
                dat +=tdata;cols +=tcolumns

                tdata, tcolumns = ling_features_from_tweet(tweet)
                dat +=tdata;cols +=tcolumns

                tdata, tcolumns = vis_features_from_tweet(tweet,tdb)
                dat +=tdata;cols +=tcolumns

                tdata, tcolumns = satnxn_features(tweet)
                dat +=tdata;cols +=tcolumns

                tdata, tcolumns = behave_features(tweet)
                dat +=tdata;cols +=tcolumns
            except Exception:
                print('Error in processing '+tdb+'/tweets/'+str(key))
                continue

            if not columns:
                pen.writerow(cols)
                columns = True
            data.append(dat)
            counter -=1
            if counter == 0:
                pen.writerows(data)
                data = list()
                gc.collect()
                print('saved!!')
                counter = TWEETS_BATCH_SIZE
        
        pen.writerows(data)
        data = list()
        gc.collect()
        file.close()
        print(tdb,'finished!!')

dbs = './DB2/raw_data/'
save_dir='./DB2/processed_data/'
threads = list()
for thread_no in range(NO_OF_THREADS):
    dirs = os.listdir(dbs)
    threads.append(Thread(target=thread_fun,args=(dbs,dirs[(thread_no*NO_OF_JOBS_PER_THREAD):((thread_no+1)*NO_OF_JOBS_PER_THREAD)],save_dir)))
    threads[-1].start()

    # break

for thread in threads:
    thread.join()
print('completed fully')
