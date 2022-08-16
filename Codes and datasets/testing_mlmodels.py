import csv

import pandas as pd
import joblib
from ml_models import make_dnn, make_svm, make_lr, make_dtree, labelof, make_knn

cae_header = ['tposemo','tnegemo','tposemoji','tnegemoji','texclaim','tqmark','t3dots','tperiod','adverb','fct1','fct2','fct3','fct4','fct5','fct6','fct7','fct8','fct9','fct10','fct11','fct12','fct13','fct14','fct15','sat_mean','sat_contrast','brit_mean','brit_contrast','warm/cool','clear/dull','replies_cnt','retweets_cnt','likes_cnt']
other_fields = ['mentions_cnt','retweet?','reply?','hour0','hour1','hour2','hour3','hour4','hour5','hour6','hour7','hour8','hour9','hour10','hour11','hour12','hour13','hour14','hour15','hour16','hour17','hour18','hour19','hour20','hour21','hour22','hour23','imagetweet?','originalTweet?','query?','sharingtweet?','ppron','home','work','money','relig','death','health','ingest','friend','family']
my_fields = ['i','we','swear','reward','achieve','affiliation','ppos','pneg','pneu']
y_fields = ['pos','neg','neu']
file_name = './data/new_selected.csv'
cae_data_file = './data/full_modalities.csv'
full_mods_file = './temp/new_selected_full.csv'
labelled1 = './data/pos_labelled.csv'
labelled2 = './data/neg_neu_labelled_bang.csv'
labelled3 = './data/neg_neu_labelled_non_bang.csv'
day_wise_with_cae = './data/a1.csv'
day_wise_with_out_cae = './data/a2.csv'
week_wise_with_cae = './data/b1.csv'
week_wise_with_out_cae = './data/b2.csv'

df1 = pd.read_csv(day_wise_with_cae)
df2 = pd.read_csv(day_wise_with_out_cae)
df3 = pd.read_csv(week_wise_with_cae)
df4 = pd.read_csv(week_wise_with_out_cae)

da1_x = df1[cae_header+other_fields].values.tolist()
da2_x = df2[cae_header+other_fields].values.tolist()
da3_x = df1[cae_header+other_fields+my_fields].values.tolist()
da4_x = df2[cae_header+other_fields+my_fields].values.tolist()

a_y = [labelof(row[0],row[1],row[2]) for row in df1[y_fields].values.tolist()]

db1_x = df3[cae_header+other_fields].values.tolist()
db2_x = df4[cae_header+other_fields].values.tolist()
db3_x = df3[cae_header+other_fields+my_fields].values.tolist()
db4_x = df4[cae_header+other_fields+my_fields].values.tolist()

b_y = [labelof(row[0],row[1],row[2]) for row in df3[y_fields].values.tolist()]
# new_data = fill_modalities(data, make_cae_from_file(cae_data_file, None))

# csv.writer(open(full_mods_file,'w',newline='')).writerows([cae_header]+new_data)

# other_data1 = df1[other_fields].values.tolist()
# other_data2 = df2[other_fields].values.tolist()
# other_data3 = df3[other_fields].values.tolist()

# y_data1 = df1[y_fields].values.tolist()
# y_data2 = df2[y_fields].values.tolist()
# y_data3 = df3[y_fields].values.tolist()

# data_x, data_y, data_id = make_format(data1+data2+data3,other_data1+other_data2+other_data3,y_data1+y_data2+y_data3)
import numpy as np
result_table = list()
result_table.append([r"model_desc",'dnn','svm','dtree','knn','lr'])

row = ['daywise with cae']
_, scores = make_dnn(da1_x,a_y);row.append(np.mean(scores))
_, scores = make_svm(da1_x,a_y);row.append(np.mean(scores))
_, scores = make_dtree(da1_x,a_y);row.append(np.mean(scores))
_, scores = make_knn(da1_x,a_y);row.append(np.mean(scores))
_, scores = make_lr(da1_x,a_y);row.append(np.mean(scores))
result_table.append(list(row))
print(row)

# row = ['daywise without cae']
# _, scores = make_cnn(da2_x,a_y);row.append(np.mean(scores))
# _, scores = make_svm(da2_x,a_y);row.append(np.mean(scores))
# _, scores = make_dtree(da2_x,a_y);row.append(np.mean(scores))
# _, scores = make_knn(da2_x,a_y);row.append(np.mean(scores))
# _, scores = make_lr(da2_x,a_y);row.append(np.mean(scores))
# result_table.append(list(row))
# print(row)

# row = ['daywise with cae with extra attr']
# _, scores = make_cnn(da3_x,a_y);row.append(np.mean(scores))
# _, scores = make_svm(da3_x,a_y);row.append(np.mean(scores))
# _, scores = make_dtree(da3_x,a_y);row.append(np.mean(scores))
# _, scores = make_knn(da3_x,a_y);row.append(np.mean(scores))
# _, scores = make_lr(da3_x,a_y);row.append(np.mean(scores))
# result_table.append(list(row))
# print(row)

# row = ['daywise without cae with extra attr']
# _, scores = make_cnn(da4_x,a_y);row.append(np.mean(scores))
# _, scores = make_svm(da4_x,a_y);row.append(np.mean(scores))
# _, scores = make_dtree(da4_x,a_y);row.append(np.mean(scores))
# _, scores = make_knn(da4_x,a_y);row.append(np.mean(scores))
# _, scores = make_lr(da4_x,a_y);row.append(np.mean(scores))
# result_table.append(list(row))
# print(row)

# row = ['weekwise with cae']
# _, scores = make_cnn(db1_x,b_y);row.append(np.mean(scores))
# _, scores = make_svm(db1_x,b_y);row.append(np.mean(scores))
# _, scores = make_dtree(db1_x,b_y);row.append(np.mean(scores))
# _, scores = make_knn(db1_x,b_y);row.append(np.mean(scores))
# _, scores = make_lr(db1_x,b_y);row.append(np.mean(scores))
# result_table.append(list(row))
# print(row)

# row = ['weekwise without cae']
# _, scores = make_cnn(db2_x,b_y);row.append(np.mean(scores))
# _, scores = make_svm(db2_x,b_y);row.append(np.mean(scores))
# _, scores = make_dtree(db2_x,b_y);row.append(np.mean(scores))
# _, scores = make_knn(db2_x,b_y);row.append(np.mean(scores))
# _, scores = make_lr(db2_x,b_y);row.append(np.mean(scores))
# result_table.append(list(row))
# print(row)

# row = ['weekwise with cae with extra attr']
# _, scores = make_cnn(db3_x,b_y);row.append(np.mean(scores))
# _, scores = make_svm(db3_x,b_y);row.append(np.mean(scores))
# _, scores = make_dtree(db3_x,b_y);row.append(np.mean(scores))
# _, scores = make_knn(db3_x,b_y);row.append(np.mean(scores))
# _, scores = make_lr(db3_x,b_y);row.append(np.mean(scores))
# result_table.append(list(row))
# print(row)

# row = ['weekwise without cae with extra attr']
# _, scores = make_cnn(db4_x,b_y);row.append(np.mean(scores))
# _, scores = make_svm(db4_x,b_y);row.append(np.mean(scores))
# _, scores = make_dtree(db4_x,b_y);row.append(np.mean(scores))
# _, scores = make_knn(db4_x,b_y);row.append(np.mean(scores))
# _, scores = make_lr(db4_x,b_y);row.append(np.mean(scores))
# result_table.append(list(row))
# print(row)

csv.writer(open('./resultstmp.csv','w',newline='')).writerows(result_table)