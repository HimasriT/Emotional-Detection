import datetime as dt

import joblib
import numpy as np
from sklearn import svm, tree
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier, MLPRegressor

import csv
first_field = lambda row:row[0]
cur_time = lambda : str(dt.datetime.now()).replace(':','_')
get_data = lambda file_name: np.loadtxt(file_name,skiprows=1,delimiter=',')
# make_cae_from_file = lambda file_name,save_to: make_cae(get_data(file_name),save_to)
# make_tweetwise_cnn_from_file = lambda file_name,save_to: make_tweetwise_cnn(get_data(file_name)[:-3],get_data(file_name)[-3:],save_to)
# mean_pool= lambda matrix: np.mean(matrix,axis=0)

# def labelof(pos, neg, neu):
#     if pos == 0 and neg == 0:
#         return 0
#     if pos > neg:
#         return 1
#     if neg >= pos:
#         return -1
#     return 0

def save_predict(model,data_x,data_y):
    data_y = np.reshape(data_y,(-1,1))
    data_y_prob = model.predict_proba(data_x)
    data_y_pred = np.reshape(model.predict(data_x),(-1,1))
    print(np.shape(data_y_prob),np.shape(data_y))
    res = np.concatenate((data_y_prob,data_y,data_y_pred),axis=1)
    csv.writer(open('./abc.csv','w',newline='')).writerows(res)
    exit()

def make_tweetwise_format(cae_data_x, train_data_x, train_data_y):
    assert len(cae_data_x) == len(train_data_x) and len(train_data_x) == len(train_data_y)
    cae_data_x = sorted(cae_data_x,key=first_field)
    train_data_x = sorted(train_data_x,key= first_field)
    train_data_y = sorted(train_data_y,key= first_field)
    data_x = list()
    data_y = list()
    data_id = list()
    for i in range(len(cae_data_x)):
        assert cae_data_x[i][0] == train_data_x[i][0] and cae_data_x[i][0] == train_data_y[i][0]
        data_x.append(cae_data_x[i][1:]+train_data_x[i][1:])
        try:
            data_y.append(1 if int(train_data_y[i][1])==1 else (-1 if int(train_data_y[i][2])==1 else (0 if int(train_data_y[i][3])==1 else 2)))
        except ValueError:
            data_y.append(2)
        data_id.append(cae_data_x[i][0])
    return data_x, data_y, data_id

def make_cae(train_data,save_to='./models/cae_model.cnn'):
    #print('Data shape:',np.shape(train_data)) 
    cae_model = MLPRegressor(hidden_layer_sizes=(1,),activation='logistic',solver='sgd', max_iter=50)
    cae_model.fit(train_data,train_data)
    print('training info:',cae_model.n_iter_,cae_model.loss_)
    if save_to is not None:
        joblib.dump(cae_model,save_to)
    return cae_model

def make_model(train_data_x, train_data_y, mlpmodel, save_to=None, cross_val=5):
    assert np.shape(train_data_x)[0] == np.shape(train_data_y)[0]
    model = OneVsRestClassifier(mlpmodel)
    if cross_val > 0 and cross_val <=10:
        scores = cross_val_score(model, train_data_x, train_data_y, cv=cross_val)
        print('scores - mean :',scores,np.mean(scores))
    model.fit(train_data_x,train_data_y)
    if save_to is not None:
        joblib.dump(model,save_to)
    return model, list(scores)

def make_knn(train_data_x, train_data_y, save_to=None, cross_val=5):
    #print('Data shape:',np.shape(train_data_x),np.shape(train_data_y))
    assert np.shape(train_data_x)[0] == np.shape(train_data_y)[0]
    model = KNeighborsClassifier(3)
    if cross_val > 0 and cross_val <=10:
        scores = cross_val_score(model, train_data_x, train_data_y, cv=cross_val)
        print('scores - mean:',scores,np.mean(scores))
    model.fit(train_data_x,train_data_y)
    if save_to is not None:
        joblib.dump(model,save_to)
    return model, list(scores)

def make_dnn(train_data_x, train_data_y, hidden_layers=1, save_to=None, cross_val=5, verbose=False):
    assert np.shape(train_data_x)[0] == np.shape(train_data_y)[0]
    mlpmodel = MLPClassifier(hidden_layer_sizes=hidden_layers*(np.shape(train_data_x)[1]+1,),max_iter=100,activation='logistic', solver='sgd',verbose=verbose)
    model = OneVsRestClassifier(mlpmodel)
    if cross_val > 0 and cross_val <=10:
        scores = cross_val_score(model, train_data_x, train_data_y, cv=cross_val)
        print('scores - mean:',scores,np.mean(scores))
    model.fit(train_data_x,train_data_y)
    if save_to is not None:
        joblib.dump(model,save_to)
    return model, list(scores)

def make_svm(train_data_x, train_data_y, save_to = None, cross_val=5, verbose = False):
    # data_shape = np.shape(train_data_x)
    # print('Data shape:',np.shape(train_data_x),np.shape(train_data_y))
    assert np.shape(train_data_x)[0] == np.shape(train_data_y)[0]
    mlpmodel = svm.SVC( probability=True,verbose=verbose)
    model = OneVsRestClassifier(mlpmodel)
    if cross_val > 0 and cross_val <=10:
        scores = cross_val_score(model, train_data_x, train_data_y, cv=cross_val)
        print('scores - mean:',scores,np.mean(scores))
    model.fit(train_data_x,train_data_y)
    if save_to is not None:
        joblib.dump(model,save_to)
    return model, list(scores)

def make_lr(train_data_x, train_data_y, save_to = None, cross_val=5):
    #print('Data shape:',np.shape(train_data_x),np.shape(train_data_y))
    assert np.shape(train_data_x)[0] == np.shape(train_data_y)[0]
    mlpmodel = LogisticRegression(max_iter=100)
    model = OneVsRestClassifier(mlpmodel)
    if cross_val > 0 and cross_val <=10:
        scores = cross_val_score(model, train_data_x, train_data_y, cv=cross_val)
        print('scores - mean:',scores,np.mean(scores))
    model.fit(train_data_x,train_data_y)
    if save_to is not None:
        joblib.dump(model,save_to)
    return model, list(scores)
def make_dtree(train_data_x, train_data_y, save_to = None, cross_val=5):
    #print('Data shape:',np.shape(train_data_x),np.shape(train_data_y))
    assert np.shape(train_data_x)[0] == np.shape(train_data_y)[0]
    mlpmodel = tree.DecisionTreeClassifier()
    model = OneVsRestClassifier(mlpmodel)
    if cross_val > 0 and cross_val <=10:
        scores = cross_val_score(model, train_data_x, train_data_y, cv=cross_val)
        print('scores - mean:',scores,np.mean(scores))
    model.fit(train_data_x,train_data_y)
    if save_to is not None:
        joblib.dump(model,save_to)
    return model,list(scores)

def fill_modalities(data_body, cae_model):
    """
        'data_body' data with out header
    """
    data_body = sorted(data_body,key=lambda row:row[0])

    ids_list = list()
    input_data = list()
    for row in data_body:
        ids_list.append(row[0])
        input_data.append(row[1:])
    result_data = cae_model.predict(input_data)
    processed_data = list()
    for i in range(len(result_data)):
        processed_data.append([ids_list[i]]+list(result_data[i]))
    return processed_data
