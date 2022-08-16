"""
    data collection tools
"""

import json
import os
import time
from datetime import datetime
from urllib.parse import urlparse
import gc

import bs4
import requests
import tweepy
from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

CREDS_FILE = './utils/secrets.json'
CREDS_ID = 'ggajam'
TWEETS_BATCH_SIZE = 100
PROXIES = {'http': 'http://172.30.0.13:3128','https': 'http://172.30.0.13:3128'}

def load(url):
    chrome = webdriver.Chrome()
    chrome.get(url)

    tag = chrome.find_element_by_tag_name('html')
    for i in range(300):
        print(i,end=' ')
        tag.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)
    print('program ended!')

def extractTweets(file_path, save_to=None):
    doc = open(file_path,encoding='utf-8')
    soup = bs(doc,'html.parser')
    items = soup.find_all('div',class_="tweet")
    tweets_list = list()
    for item in items:
        try:
            tweets_list.append(item.attrs['data-permalink-path'])
        except KeyError:
            pass
    data_dict = dict()
    for link in tweets_list:
        arr = str(link).split('/')
        if arr[1] not in data_dict.keys():
            data_dict[str(arr[1])] = list()
        data_dict[str(arr[1])].append(str(arr[3]))
    if save_to is not None:
        json.dump(data_dict,open(save_to,'w'))
    return data_dict

def mk_db_dir(loc):
    try:
        os.makedirs(loc+'/tweets/')
    except FileExistsError:
        print(loc+'/tweets/ already exists!')

    try:
        os.makedirs(loc+'/media/')
    except FileExistsError:
        print(loc+'/media/ already exists')

    if not os.path.isfile(loc+'/metadata.json'):
        fd = open(loc+'/metadata.json','w')
        fd.write('{}')
        fd.close()

def reply_count(user, tweet_id, log_fd=None):
        """
            returns reply count of the tweet
        """
        res = requests.get('https://twitter.com/' + user + '/status/' + tweet_id)
        try:
            res.raise_for_status()
        except Exception as exc:
            if log_fd is not None:
                log_fd.write('There was a problem: %s\n' % (exc))
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        return soup.select('span[data-tweet-stat-count]')[0].attrs['data-tweet-stat-count']

def get_reply_counts(file_path):
    metadata = json.load(open(file_path))
    counter = TWEETS_BATCH_SIZE
    
    for key in metadata:
        if 'reply_count' not in metadata[key]:
            print(key)
            try:
                metadata[key]['reply_count'] = reply_count(metadata[key]['user'], key)
            except Exception as info:
                print(info)
                metadata[key]['reply_count'] = 0
            counter -=1
            if counter == 0:
                json.dump(metadata, open(file_path,'w'))
                counter = TWEETS_BATCH_SIZE
                print('saved!!')
    json.dump(metadata, open(file_path,'w'))
    print('finished!!')

def combine_metadata(file1, file2, combinedfile = None):
    """
        combines two metadata files (file1, file2)
        stores in combinedfile
        if not given stores in file1
    """
    metadata1 = json.load(open(file1))
    metadata2 = json.load(open(file2))
    for key in metadata2.keys():
        if key in metadata1.keys():
            metadata1[key]['containsImage'] = metadata1[key]['containsImage'] or metadata2[key]['containsImage']
            metadata1[key]['label'] = str(metadata1[key]['label'] or metadata2[key]['label'])
            metadata1[key]['processed'] = metadata1[key]['processed'] or metadata2[key]['processed']
        else:
            metadata1[key] = metadata2[key]
    print('total keys:', len(metadata1.keys()))
    if combinedfile is None:
        json.dump(metadata1,open(file1,'w'))
    else:
        json.dump(metadata1,open(combinedfile,'w'))

def init_api (creds_path=CREDS_FILE, app_only=True):
    creds = json.load(open(creds_path))[CREDS_ID]
    auth = tweepy.OAuthHandler(creds['consumer_key'], creds['consumer_secret'])
    if not app_only:
        auth.set_access_token(creds['access_token'], creds['access_token_secret'])
    api = tweepy.API(auth,wait_on_rate_limit=True,retry_count=10,proxy=PROXIES['https'],wait_on_rate_limit_notify=True)
    return api

    
def save_tweet(tweet, loc, metadata, log_fd=None):
    """
        saves the tweet at loc
    """
    if 'possibly_sensitive' in tweet.keys() and tweet['possibly_sensitive']:
        return False
    id_str = tweet['id_str']
    if not os.path.isfile(loc+'tweets/'+id_str+'.json'):
        json.dump(tweet, open(loc+'tweets/'+id_str+'.json', mode='w'))
    elif log_fd is not None:
        print(id_str+' is already present!!');log_fd.write(id_str+' is already present!!\n')

    if log_fd is not None:
        log_fd.write(id_str+'\n')

    if id_str not in metadata.keys():
        metadata[id_str] = dict()
    try:
        if 'extended_entities' in tweet and 'media' in tweet['extended_entities']:
            for media in tweet['extended_entities']['media']:
                if media['type'] == 'photo':
                    url_pkt = urlparse(media['media_url'])
                    with open(loc+url_pkt.path, 'wb') as imagef:
                        for chunk in requests.get(url_pkt.geturl(),proxies=PROXIES).iter_content(100000):
                            imagef.write(chunk)
                    # metadata[id_str]['containsImage'] = True
                    break
            # if 'containsImage' not in metadata[id_str].keys():
            #     metadata[id_str]['containsImage'] = False
    except Exception as info:
        print(info)
        # if 'containsImage' not in metadata[id_str].keys():
        #     metadata[id_str]['containsImage'] = False
        if log_fd is not None:
            log_fd.write(str(info)+'\n')

    # try:
    #     metadata[id_str]['retweet'] = bool('retweeted_status' in tweet.keys() and tweet['retweeted_status'] is not None)
    # except Exception as info:
    #     print(info)
    #     metadata[id_str]['retweet'] = False
    #     if log_fd is not None:
    #         log_fd.write(str(info)+'\n')

    # try:
    #     metadata[id_str]['reply'] = bool(tweet['in_reply_to_status_id'] is not None)
    # except Exception as info:
    #     print(info)
    #     metadata[id_str]['reply'] = False
    #     if log_fd is not None:
    #         log_fd.write(str(info)+'\n')

    # try:
    #     metadata[id_str]['quote'] = bool('quoted_status' in tweet.keys() and len(tweet['quoted_status']) > 0)
    # except Exception as info:
    #     print(info)
    #     metadata[id_str]['quote'] = False
    #     if log_fd is not None:
    #         log_fd.write(str(info)+'\n')
    
    metadata[id_str]['user'] = tweet['user']['screen_name']
    if log_fd is not None:
            log_fd.write('saved \n')
    return metadata

def by_tweet(tweet_id, label, api, loc='./twitter_db/by_tweet/'):
    """
        collects the tweet and stores
    """
    mk_db_dir(loc)
    metadata = json.load(open(loc+'metadata.json'))
    with open('./logs/by_tweet '+str(datetime.now()).replace(':','-')+'.log', 'w') as log_fd:
        print(tweet_id+' '+str(label));log_fd.write(tweet_id+' '+str(label)+'\n')
        try:
            save_tweet(api.get_status(tweet_id)._json, loc, metadata, log_fd)
        except Exception as err:
            print(err);log_fd.write(str(err)+'\n')
        finally:
            json.dump(metadata, open(loc+'metadata.json', mode='w'))
            log_fd.write('updated metadata\n')

def by_user(user, api, since_id,max_id,db_loc):
    """
    	Collects tweets of a "user" from "since_id" to "max_id" and
    	stores in "db_loc" in an organized structure
		api is an object that takes care of authentication to twitter APIs
    """
    loc = db_loc+user+'/' 
    mk_db_dir(loc)
    metadata = json.load(open(loc+'metadata.json'))
    counter = TWEETS_BATCH_SIZE # setting counter to TWEETS_BATCH_SIZE
    gc.enable() # enabling garbage collection
    tweet_cnt =0 # no of tweets collected
    with open('./logs/by_user '+str(datetime.now()).replace(':','-')+'.log', 'w') as log_fd: # log file
        log_fd.write(user+' '+since_id+' '+max_id+' '+loc+'\n')
        try:
            for tweet in tweepy.Cursor(api.user_timeline, id=user, since_id=since_id, max_id=max_id).items():
                print(tweet._json['id_str']);log_fd.write(tweet._json['id_str']+'\n')
                if tweet._json['id_str'] not in metadata.keys():
                    save_tweet(tweet._json, loc, metadata, log_fd) # saves the tweet json object at "loc"
                    tweet_cnt +=1
                    counter -=1
                    if counter == 0:
                        counter = TWEETS_BATCH_SIZE
                        json.dump(metadata, open(loc+'metadata.json', mode='w')) # saving the metadata for RAM optimal utilization
                        gc.collect() # garbage collection is done here
                        print('saved!!');log_fd.write('saved!!\n')
        except Exception as err:
            print(err);log_fd.write(str(err)+'\n')
        finally:
            json.dump(metadata, open(loc+'metadata.json', mode='w'))
            print('updated metadata');log_fd.write('updated metadata\n')
    print(str(tweet_cnt)+" are collected from "+str(user))


def by_query(qry, label, cnt, api, loc='./twitter_db/by_query/'):
    """
        search twitter
    """
    mk_db_dir(loc)
    with open('./logs/by_query '+str(datetime.now()).replace(':','-')+'.log', 'w') as log_fd:
        log_fd.write(qry+' '+str(label)+' '+str(cnt)+' '+loc+'\n')
        metadata = json.load(open(loc+'metadata.json'))
        for status in tweepy.Cursor(api.search, q=qry, lang='en').items(cnt):
            save_tweet(status._json, loc, metadata, log_fd)
        json.dump(metadata, open(loc+'metadata.json', mode='w'))
        log_fd.write('updated metadata\n')

def image_tweets_by_query(qry, label, cnt, api, loc='./twitter_db/image_tweets_by_query/'):
    """
        search twitter
    """
    mk_db_dir(loc)
    with open('./logs/by_query '+str(datetime.now()).replace(':','-')+'.log', 'w') as log_fd:
        log_fd.write(qry+' '+str(label)+' '+str(cnt)+' '+loc+'\n')
        metadata = json.load(open(loc+'metadata.json'))
        for status in tweepy.Cursor(api.search, q=qry).items():
            if cnt > 0:
                try:
                    tweet = status._json
                    for media in tweet['extended_entities']['media']:
                        if media['type'] == 'photo' and \
                            len(tweet['text']) > 0 and \
                            tweet['id_str'] not in metadata.keys() and\
                            save_tweet(tweet, loc, metadata, log_fd):
                                cnt = cnt - 1
                                log_fd.write(str(cnt)+'\n')
                                print(cnt)
                except KeyError:
                    pass
            else:
                break
        json.dump(metadata, open(loc+'metadata.json', mode='w'))
        log_fd.write('updated metadata\n')
    
def fix_metadata(loc, api):
    with open('./logs/fix_metadata'+str(datetime.now()).replace(':','-')+'.log','w') as log_fd:
        log_fd.write('fix_metadata '+loc+'\n')
        try:
            metadata = json.load(open(loc+'/metadata.json'))
        except Exception:
            metadata = dict()

        for x in os.listdir(loc+'./tweets'):
            if str(x[:-5]) not in metadata.keys():
                log_fd.write(x[:-5]+'\n')
                metadata[str(x[:-5])] = {}
        
        json.dump(metadata, open(loc+'metadata.json','w'))
        print('metadata fixed....');log_fd.write('metadata fixed..\n')
        
        dirtweets = os.listdir(loc+'./tweets')
        try:
            for x in metadata.keys():
                log_fd.write(x+'\n')    
                if (x+'.json') not in dirtweets:
                    metadata = save_tweet(api.get_status(x)._json, loc, metadata, log_fd)
                else:
                    metadata = save_tweet(json.load(open(loc+'/tweets/'+x+'.json')),loc, metadata, log_fd)
        finally:    
            json.dump(metadata, open(loc+'metadata.json','w'))
        print('tweets dir is fixed..');log_fd.write('tweets dir is fixed..\n')

def removescrap(loc):
    with open('./logs/removescrap '+str(datetime.now()).replace(':','-')+'.log','w') as log_fd:
        log_fd.write('removescrap '+loc+'\n')
        fix_metadata(loc, init_api())
        metadata =json.load(open(loc+'/metadata.json'))
        selected_list = list()
        for x in metadata.keys():
            tweet = json.load(open(loc+'/tweets/'+x+'.json'))
            if 'possibly_sensitive' in tweet.keys() and tweet['possibly_sensitive']:
                selected_list =  selected_list + [x]
            elif metadata[x]['containsImage']:
                for media in tweet['extended_entities']['media']:
                    if media['type'] == 'photo':
                        url_pkt = urlparse(media['media_url'])
                        if not os.path.exists(loc+'/'+url_pkt.path):
                            # print(loc+url_pkt.path)
                            selected_list = selected_list + [x]
                            break
        for x in selected_list:
            tweet = json.load(open(loc+'/tweets/'+x+'.json'))
            if metadata[x]['containsImage']:
                for media in tweet['extended_entities']['media']:
                    if media['type'] == 'photo':
                        url_pkt = urlparse(media['media_url'])
                        if os.path.exists(loc+'/'+url_pkt.path):
                            os.remove(loc+'/'+url_pkt.path)
            if os.path.exists(loc+'/tweets/'+x+'.json'):
                os.remove(loc+'/tweets/'+x+'.json')
            if x in metadata.keys():
                del metadata[x]
            log_fd.write(x+'\n')
            # print(x)
        json.dump(metadata,open(loc+'/metadata.json','w'))
        log_fd.write('updated metadata\n')
