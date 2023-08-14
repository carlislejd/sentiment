import time
import re, string
import pandas as pd
from datetime import datetime, timedelta



def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x
    flatten(y)
    return out


def tweet_history(screen_name, days, client, api):
    user_id = api.get_user(screen_name=screen_name)['id']
    start_time = (str((datetime.utcnow() + timedelta(days=-days)).isoformat())[0:23] + 'Z')

    all_raw = []

    tweets = client.get_users_tweets(id=user_id, tweet_fields=['created_at', 'public_metrics'], expansions=['author_id'], user_fields=['id'], exclude='replies', start_time=start_time, max_results=100)
    for tweet in tweets[0]:
        all_raw.append(tweet.data)

    if 'next_token' in tweets.meta:
        updated_token = tweets.meta['next_token']
        while 'next_token' in tweets.meta:
            tweets = client.get_users_tweets(id=user_id, tweet_fields=['created_at', 'public_metrics'], pagination_token=updated_token, expansions=['author_id'], user_fields=['id'], exclude='replies', start_time=start_time, max_results=100)
            if tweets.meta['result_count'] > 0:            
                for tweet in tweets[0]:
                    all_raw.append(tweet.data)
                if 'next_token' in tweets.meta:
                    updated_token = tweets.meta['next_token']
                else: 
                    break
                time.sleep(1)
            else:
                break

    final_raw = []
    for each in all_raw:
        final_raw.append(flatten_json(each))
    twitter_df = pd.DataFrame(final_raw).reset_index(drop=True)

    now = datetime.utcnow()
    now = now.replace(minute = 0, second = 0, microsecond = 0)
    twitter_df['ts'] = now
    twitter_df['ts_date'] = pd.to_datetime(twitter_df['ts'], utc=True).dt.strftime('%Y-%m-%d')
    twitter_df['ts'] = pd.to_datetime(twitter_df['ts'], utc=True).dt.strftime('%Y-%m-%d %H:%M:%S')

    twitter_df['url'] = 'https://twitter.com/' + twitter_df['author_id'].astype(str) + '/status/' + twitter_df['id']
    twitter_df['platform'] = 'twitter'
    twitter_df['timestamp'] = twitter_df.created_at.apply(lambda x: x.replace('T',' ').replace('Z',''))
    twitter_df['created_ts'] = pd.to_datetime(twitter_df['timestamp'], utc=True).dt.strftime('%Y-%m-%d %H:%M:%S')
    twitter_df['created_date'] = pd.to_datetime(twitter_df['timestamp'], utc=True).dt.strftime('%Y-%m-%d')
    twitter_df = twitter_df[['ts','ts_date','created_ts','created_date','platform','author_id','id','like_count','reply_count','retweet_count','quote_count','text','url']]
    twitter_df.columns = ['ts','ts_date','created_ts','created_date','platform','author_id','tweet_id','like_count','reply_count','retweet_count','quote_count','tweet','tweet_url']
    return twitter_df


#Remove punctuations, links, mentions and \r\n new line characters
def strip_all_entities(text): 
    text = text.replace('\r', '').replace('\n', ' ').replace('\n', ' ').lower() #remove \n and \r and lowercase
    text = re.sub(r"(?:\@|https?\://)\S+", "", text) #remove links and mentions
    text = re.sub(r'[^\x00-\x7f]',r'', text) #remove non utf8/ascii characters such as '\x9a\x91\x97\x9a\x97'
    banned_list= string.punctuation + 'Ã'+'±'+'ã'+'¼'+'â'+'»'+'§'
    table = str.maketrans('', '', banned_list)
    text = text.translate(table)
    return text

#clean hashtags at the end of the sentence, and keep those in the middle of the sentence by removing just the # symbol
def clean_hashtags(tweet):
    new_tweet = " ".join(word.strip() for word in re.split('#(?!(?:hashtag)\b)[\w-]+(?=(?:\s+#[\w-]+)*\s*$)', tweet)) #remove last hashtags
    new_tweet2 = " ".join(word.strip() for word in re.split('#|_', new_tweet)) #remove hashtags symbol from words in the middle of the sentence
    return new_tweet2

#Filter special characters such as & and $ present in some words
def filter_chars(a):
    sent = []
    for word in a.split(' '):
        if ('$' in word) | ('&' in word):
            sent.append('')
        else:
            sent.append(word)
    return ' '.join(sent)

def remove_mult_spaces(text): # remove multiple spaces
    return re.sub("\s\s+" , " ", text)
