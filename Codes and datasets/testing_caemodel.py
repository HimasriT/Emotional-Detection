import pandas as pd
from ml_models import make_cae
import joblib
import csv
header = ['posemo','negemo','posemoji','negemoji','exclaim','qmark','3dots','period','deg_adv','adv_cnt','fct1','fct2','fct3','fct4','fct5','fct6','fct7','fct8','fct9','fct10','fct11','fct12','fct13','fct14','fct15','sat_mean','sat_contrast','brit_mean','brit_contrast','warm_cool','clear_dull','replies_cnt','retweets_cnt','likes_cnt']

new_header = ['f'+ele for ele in header]
print(new_header)
exit()
# db1_file = './datasets/db1_full_mods.csv'
# db2_file = './datasets/db2_full_mods.csv'

# df1 = pd.read_csv(db1_file)[header].values.tolist()
# df2 = pd.read_csv(db2_file)[header].values.tolist()

# data = df1+df2
# print(len(data),len(data[0]))
# model = make_cae(data)
# print('model is made!!')
# joblib.dump(model,'./models/cae.cnn')
# print('model is dumped!!')

db2_tweet_attrs = './datasets/db2_tweet_attrs.csv' 
model = joblib.load('./models/cae.cnn')
df3 = pd.read_csv(db2_tweet_attrs)
data_ = df3[header]
data_f =list(model.predict(data_))
ids = df3['id_str']

new_header = ['id_str']+['f'+ele for ele in header]
data_id = list()
print('making format')
for i in range(len(data_f)):
    data_id.append(list(data_f[i]))
    data_id[-1].insert(0,ids[i])
data_id.insert(0,new_header)
print('dumping')
csv.writer(open('./DB2/caeed_data.csv','w',newline='')).writerows(data_id)

