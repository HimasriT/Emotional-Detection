import csv

import joblib
import numpy as np
import pandas as pd
import pprint
from ml_models import make_dnn, make_dtree, make_knn, make_lr,make_svm, save_predict
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import normalize
import warnings
from sklearn.exceptions import ConvergenceWarning

SPLIT_RATIO = 0.7

datafile = './datasets/db2_tweets_totalc.csv'
warnings.filterwarnings(action='ignore', category=ConvergenceWarning)

pp = pprint.PrettyPrinter(indent=4)
tweet_attr = ['fposemo','fnegemo','fposemoji','fnegemoji','fperiod','fqmark','fexclaim','f3dots','fdeg_adv','fadv_cnt','ffct1','ffct2','ffct3','ffct4','ffct5','ffct6','ffct7','ffct8','ffct9','ffct10','ffct11','ffct12','ffct13','ffct14','ffct15','fsat_mean','fsat_contrast','fbrit_mean','fbrit_contrast','fwarm_cool','fclear_dull','freplies_cnt','fretweets_cnt','flikes_cnt']
# tweet_attrs = ['posemo','negemo','posemoji','negemoji','period','qmark','exclaim','3dots','deg_adv','adv_cnt','fct1','fct2','fct3','fct4','fct5','fct6','fct7','fct8','fct9','fct10','fct11','fct12','fct13','fct14','fct15','sat_mean','sat_contrast','brit_mean','brit_contrast','warm_cool','clear_dull','replies_cnt','retweets_cnt','likes_cnt']
behave = ['mentions_cnt','retweet_cnt','reply_cnt','hour0','hour1','hour2','hour3','hour4','hour5','hour6','hour7','hour8','hour9','hour10','hour11','hour12','hour13','hour14','hour15','hour16','hour17','hour18','hour19','hour20','hour21','hour22','hour23','imagetweet_cnt','originalTweet_cnt','query_cnt','sharingtweet_cnt']
liwc_cat = ['ppron','home','work','money','relig','death','health','ingest','friend','family']
liwc_xtra = ['reward','achieve','affiliation','swear']
prons = ['i','you','shehe','we','they']
replies = ['rfamily','rfriend','rposemo','raffect','rleisure','rsad','rdeath','rauxverb','ranger','rnegemo','rposemoji','rnegemoji']
# past_tweets = ['ppos','pneg','pneu']

def load_full_data(file_name):
    df = pd.read_csv(file_name)
    data_tweet = (df[tweet_attr].values)
    data_pron = np.array([ [row[0]+row[1]+row[2] , row[3]+row[4]] for row in df[prons].values])
    data_behave_liwc = df[behave+liwc_cat+replies].values
    data_x = (np.append(np.append(data_tweet,data_pron,axis=1),data_behave_liwc,axis=1))
    data_y = (df['label'].values)
    return data_x, data_y

def load_data(file_name):
    
    df = pd.read_csv(file_name) 

    print(np.shape(df))
    pos = (df['label'] == 1)
    neg = (df['label'] ==-1)
    neu = (df['label'] == 0)
    
    sets = [df[pos],df[neg],df[neu]]

    train_x = list()
    train_y = list()
    test_x = list()
    test_y = list()

    for pos_sets in sets: 
        data_tweet = (pos_sets[tweet_attr].values)[:int(SPLIT_RATIO*len(pos_sets))]
        data_pron = np.array([ [row[0]+row[1]+row[2] , row[3]+row[4]] for row in pos_sets[prons].values])[:int(SPLIT_RATIO*len(pos_sets))]
        data_behave_liwc = pos_sets[behave+liwc_cat+replies].values[:int(SPLIT_RATIO*len(pos_sets))]
        train_x.append(np.append(np.append(data_tweet,data_pron,axis=1),data_behave_liwc,axis=1))
        train_y.append(pos_sets['label'].values[:int(SPLIT_RATIO*len(pos_sets))])

        data_tweet = (pos_sets[tweet_attr].values)[int(SPLIT_RATIO*len(pos_sets)):]
        data_pron = np.array([ [row[0]+row[1]+row[2] , row[3]+row[4]] for row in pos_sets[prons].values])[int(SPLIT_RATIO*len(pos_sets)):]
        data_behave_liwc = pos_sets[behave+liwc_cat+replies].values[int(SPLIT_RATIO*len(pos_sets)):]
        test_x.append( np.append(np.append(data_tweet,data_pron,axis=1),data_behave_liwc,axis=1))
        test_y.append(pos_sets['label'].values[int(SPLIT_RATIO*len(pos_sets)):])
        print(np.shape(train_x[-1]),np.shape(train_y[-1]),np.shape(test_x[-1]),np.shape(test_y[-1]))
    
    return np.concatenate(train_x), np.concatenate(train_y),np.concatenate(test_x), np.concatenate(test_y)
    
    # data_tweet = df[tweet_attr].values/7
    # data_pron = np.array([ [row[0]+row[1]+row[2] , row[3]+row[4]] for row in df[prons].values])
    # data_behave_liwc = df[behave+liwc_cat+replies+past_tweets].values
    # data_x = np.append(np.append(data_tweet,data_pron,axis=1),data_behave_liwc,axis=1)
    # data_y = df['label'].values

    # test_x,train_y,train_y = 
    # exit()
    # return np.array(data_x),np.array(data_y)



# train_data_x,train_data_y,test_data_x,test_data_y = load_data(weekfile)
# print(np.shape(train_data_x),np.shape(train_data_y),np.shape(test_data_x),np.shape(test_data_y))
# exit()
accuracy_data = np.zeros(5)
cm_data = dict() 
for i in range(5):
    cm_data[i] = dict()
    for j in range(2):
        cm_data[i][j] = [0.0,0.0]
# print(cm_data)
precision_data_pos = np.zeros(5)
precision_data_neg = np.zeros(5)
precision_data_neu = np.zeros(5)

recall_data_pos = np.zeros(5)
recall_data_neg = np.zeros(5)
recall_data_neu = np.zeros(5)

fscore_data_pos = np.zeros(5)
fscore_data_neg = np.zeros(5)
fscore_data_neu = np.zeros(5)

"""
    rows = dtree, knn, lr, dnn , svm
    columns =  weekwise, daywise
"""



train_data_x,train_data_y,test_data_x,test_data_y = load_data(datafile)
data_x,data_y = load_full_data(datafile)

print(np.shape(train_data_x),np.shape(train_data_y),np.shape(test_data_x),np.shape(test_data_y))


print('Dnn:')
model,scores = make_dnn(train_data_x,train_data_y)
accuracy_data[3] = float(np.mean(scores))
cm_data[3]=(confusion_matrix(test_data_y, model.predict(test_data_x),[1,-1,0]))
# save_predict(model,data_x, data_y);exit()

print('svm:')
model,scores = make_svm(train_data_x,train_data_y)
accuracy_data[4] = float(np.mean(scores))
cm_data[4]=(confusion_matrix(test_data_y, model.predict(test_data_x),[1,-1,0]))
# save_predict(model,data_x, data_y);exit()


print('dtree:')
model,scores = make_dtree(train_data_x,train_data_y)
accuracy_data[0] = float(np.mean(scores))
cm_data[0]=(confusion_matrix(test_data_y, model.predict(test_data_x),[1,-1,0]))
# save_predict(model,data_x, data_y);exit()


print('knn:')
model,scores = make_knn(train_data_x,train_data_y)
accuracy_data[1] = float(np.mean(scores))
cm_data[1]=(confusion_matrix(test_data_y, model.predict(test_data_x),[1,-1,0]))
# save_predict(model,data_x, data_y);exit()

print('lr:')
model,scores = make_lr(train_data_x,train_data_y)
accuracy_data[2] = float(np.mean(scores))
cm_data[2]=(confusion_matrix(test_data_y, model.predict(test_data_x),[1,-1,0]))
# save_predict(model,data_x, data_y);exit()



# else:
#     print('Day wise:')
#     data_y = np.reshape(np.concatenate((data_y,data_y_1,data_y_2,data_y_3,data_y_4,data_y_5)),(-1,len(data_y_1)))
#     csv.writer(open('./datasets/db2_daywise_labels.csv','w',newline='')).writerows(np.transpose(data_y))
    
pp.pprint(cm_data)

for mid in range(5):
    recall_data_pos[mid] = cm_data[mid][0][0]/np.sum(cm_data[mid][0])
    recall_data_neg[mid] = cm_data[mid][1][1]/np.sum(cm_data[mid][1])
    recall_data_neu[mid] = cm_data[mid][2][2]/np.sum(cm_data[mid][2])

    den = cm_data[mid][0][0]+cm_data[mid][1][1]+cm_data[mid][2][2]
    
    precision_data_pos[mid] = cm_data[mid][0][0]/np.sum(cm_data[mid][:,0])
    precision_data_neg[mid] = cm_data[mid][1][1]/np.sum(cm_data[mid][:,1])
    precision_data_neu[mid] = cm_data[mid][2][2]/np.sum(cm_data[mid][:,2])

    fscore_data_pos[mid] = 2*recall_data_pos[mid]*precision_data_pos[mid]/(recall_data_pos[mid]+precision_data_pos[mid])
    fscore_data_neg[mid] = 2*recall_data_neg[mid]*precision_data_neg[mid]/(recall_data_neg[mid]+precision_data_neg[mid])
    fscore_data_neu[mid] = 2*recall_data_neu[mid]*precision_data_neu[mid]/(recall_data_neu[mid]+precision_data_neu[mid])
        
print('accuracy:')
print(accuracy_data)

print('recall:')
print(recall_data_pos)
print(recall_data_neg)
print(recall_data_neu)

print('precision:')
print(precision_data_pos)
print(precision_data_neg)
print(precision_data_neu)

print('f-score:')
print(fscore_data_pos)
print(fscore_data_neg)
print(fscore_data_neu)

# results_file = './results/accuracies.csv'
# csv.writer(open(results_file,'w',newline='')).writerow(accuracy_data)

from conf_matrix import plot_confusion_matrix,plt
plt.figure()
plot_confusion_matrix(cm_data[4], classes=['positive','negative','neutral'],title='SVM confusion matrix')
plt.show()

# csv.writer(open('./results/recall.csv','w',newline='')).writerows()