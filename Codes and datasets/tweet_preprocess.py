import datetime as dt

from urllib.parse import urlparse

import cv2
import numpy as np
import spacy
from textblob import TextBlob

from liwc_tools import word_counter

NLP = spacy.load('en')
ANALYSER = word_counter()
TF = "%a %b %d %H:%M:%S %z %Y"
import re
WORD_REGEX =   re.compile(r"[^\n\t ]+")
# string = """venu     gopal    gajam
# i am just testing this regex            
# very good       ?
# https://venugopalgajam.website/"""
# ' '.join(WORD_REGEX.findall(string))

isReply = lambda tweet: tweet['in_reply_to_status_id'] is not None
isQuoted = lambda tweet: 'quoted_status_id_str' in tweet.keys() and len(tweet['quoted_status_id_str']) >0
isRetweet = lambda tweet: 'retweeted_status' in tweet.keys()
isSensitive = lambda tweet: 'possibly_sensitive' in tweet.keys() and tweet['possibly_sensitive'] is not None
ling_features_from_tweet = lambda tweet: ling_features(tweet['text'])
vis_features_from_path = lambda pic_path: vis_features(cv2.imread(pic_path, -1))# pylint: disable=E1101

def degree(text):
    """
        1-3 to represent neutral, moderate, and
        severe degree of positive emotions, and the minus to represent the negative
        ones
    """
    pol = TextBlob(text).polarity * 3
    arr = [-2, -1, 0]
    for i in arr:
        if pol < i:
            return i-1
    arr = [2, 1, 0]
    for i in arr:
        if pol > i:
            return i+1
    return 0

def adv_result(text):
    tweet_degree = degree(text)
    adv_tot = 0
    adj_cnt = 0
    tokens = NLP(text)
    for token in tokens:
        if token.dep_ == 'advmod':
            adv_tot = adv_tot+1
            if degree(token.head.text) == tweet_degree:
                adj_cnt = adj_cnt +1
        # print(token, token.dep_, token.head, token.head.pos_)
    if adv_tot:
        return [(tweet_degree*adj_cnt)/adv_tot, adj_cnt]
    else:
        return [0, 0]

def containsText(text):
    tokens = WORD_REGEX.findall(text)
    for token in tokens:
        if str(token).startswith('http://') or str(token).startswith('https://') or str(token).startswith('@') or str(token) == 'RT':
            continue
        else:
            return True
    return False

def ling_features(text):
    """----------------- lingistic ------------------
        0 -> containsText?
        1 -> degree adverb
        2 -> cnt of emotion words
    """
    result = list([0]*3)
    columns = ['containsText','deg_adv','adv_cnt']
    result[0] = int(containsText(text))
    if result[0]==1:
        result[1:3] = adv_result(text)
    return list(result),list(columns)    

def atostr(arr):
    """
        converts 1-d array to string for using as key
    """
    res = ''
    for i in arr:
        res = res + '|' + str(i)
    return res

def five_color_theme(hsv_mat):
    """five color theme attributes
    """
    attr_list = list([0]*15)
    pdict = dict()
    for i in np.reshape(hsv_mat, (-1, 3)):
        tmp = atostr(i)
        if tmp in pdict.keys():
            pdict[tmp][0] = pdict[tmp][0] + 1
        else:
            pdict[tmp] = [0, i]
    plist = sorted(pdict.values(), key=lambda x: x[0], reverse=True)

    tmp_list = list()
    no_of_items = min([5, len(plist)])
    for i in plist[:no_of_items]:
        tmp_list.append([i[1]])
    attr_list[:no_of_items * 3] = np.reshape(tmp_list, (-1)).tolist()
    return list(attr_list)

def containsImage(tweet):
    if 'extended_entities' in tweet.keys() and 'media' in tweet['extended_entities'].keys():
        for ele in tweet['extended_entities']['media']:
            if ele['type'] == 'photo':
                return True
    return False
def vis_features_from_tweet(tweet, twitter_db):
    pic_path = ''
    if 'extended_entities' in tweet.keys() and 'media' in tweet['extended_entities'].keys():
        for ele in tweet['extended_entities']['media']:
            if ele['type'] == 'photo':
                pic_path=str(twitter_db+urlparse(ele['media_url']).path)
                break
    return vis_features_from_path(pic_path)
def vis_features(mat):
    """------------------ visual --------------------
        0 -> containsImage?
        1-15 -> five-color theme
        16-17 -> mean value of saturation and its contrast
        18-19 -> mean value of brightness and its contrast
        20 -> warm/cool: Ratio of cool colors with hue ([0-360]) in the HSV space in [30, 110]
        or for hue([0,255]) in [21.25,77.917]
        21 -> ratio of colors with brightness and saturation
    """
    columns = ['containsImage','fct1','fct2','fct3','fct4','fct5','fct6','fct7','fct8','fct9','fct10','fct11','fct12','fct13','fct14','fct15','sat_mean','sat_contrast','brit_mean','brit_contrast','warm_cool','clear_dull']
    result = list([0]*22)
    if type(mat) == type(None):
        return list(result), list(columns)
    else:
        result[0]=1
    hsv_mat = cv2.cvtColor(mat, cv2.COLOR_BGR2HSV) # pylint: disable=E1101
    
    hue_constr = [21.5, 77.917]
    result[1:16] = five_color_theme(hsv_mat)

    [_, result[16], result[18]] = np.mean(hsv_mat, axis=(0, 1))
    [_, result[17], result[19]] = np.amax(hsv_mat, axis=(0, 1))-np.amin(hsv_mat, axis=(0, 1))

    neum = set()
    den = set()
    for i in range(np.shape(mat)[0]):
        for j in range(np.shape(mat)[1]):
            if mat[i][j][0] < mat[i][j][2]:
                den.add(atostr(mat[i][j]))
                if hsv_mat[i][j][0] >= hue_constr[0] and hsv_mat[i][j][0] <= hue_constr[1]:
                    neum.add(atostr(mat[i][j]))
    if len(den) != 0:
        result[20] = len(neum) / len(den)

    neum = set()
    den = set()
    for i in np.reshape(hsv_mat, (-1, 3)):
        den.add(atostr(i))
        if i[1] < 0.6*255:
            neum.add(atostr(i))
    if len(den) != 0:
        result[21] = len(neum) / len(den)
    return list(result),list(columns)

def satnxn_features(tweet, metadata=None):
    """------------------ social ---------------------
        0 -> containsSocial?
        1 -> comments/reply count
        2 -> retweets count
        3 -> likes/favorites count
    """
    columns = ['containsSocial','replies_cnt','retweets_cnt','likes_cnt']
    result = list([0]*4)
    if 'reply_count' in tweet:
        result[1] = int(tweet['reply_count'])
    elif metadata is not None and 'reply_count' in metadata:
        result[1] = int(metadata['reply_count'])
    result[2] = int(tweet['retweet_count'])
    result[3] = int(tweet['favorite_count'])
    result[0] = int(result[1] != 0 or result[2] != 0 or result[2] != 0)
    return list(result),list(columns)

def behave_features(tweet):
    """
    """
    columns = ['mentions_cnt','retweet_cnt','reply_cnt','hour0','hour1','hour2','hour3','hour4','hour5','hour6','hour7','hour8','hour9','hour10','hour11','hour12','hour13','hour14','hour15','hour16','hour17','hour18','hour19','hour20','hour21','hour22','hour23','imagetweet_cnt','originalTweet_cnt','query_cnt','sharingtweet_cnt'] 
    result =list([0]*31)
    if 'entities' in tweet.keys() and 'user_mentions' in tweet['entities'].keys():
        result[0] = len(tweet['entities']['user_mentions'])
    result[1] = int(isRetweet(tweet))
    result[2] = int(isReply(tweet))
    time = dt.datetime.strptime(tweet['created_at'], TF)
    result[3+int(time.hour)] = 1
    result[27] = int(containsImage(tweet))
    result[28] = int(not isRetweet(tweet) and not isQuoted(tweet) and isReply(tweet))
    result[29] = int('?' in tweet['text'])
    result[30] = int('entities' in tweet.keys() and 'urls' in tweet['entities'] and len(tweet['entities']['urls'])>0 )
    cnts, cats = ANALYSER.word_count(tweet['text'])
    return list(result+cnts),list(columns+cats)
    
def tweet_stats(tweet):
    columns = ['id_str','user_id','tdate','ttime','text','reply_to']
    result = list()
    result.append('ID'+tweet['id_str'])
    result.append(tweet['user']['screen_name'])
    result.append(str(dt.datetime.strptime(tweet['created_at'], TF).date().strftime(r"%Y-%m-%d")))
    result.append(str(dt.datetime.strptime(tweet['created_at'], TF).time()))
    result.append(str(' '.join(WORD_REGEX.findall(tweet['text']))))
    result.append('ID'+str(tweet['in_reply_to_status_id']))
    assert len(columns)==len(result) 
    return list(result), list(columns)
