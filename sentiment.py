import emoji
import tweepy
import pandas as pd
from os import getenv
from dotenv import load_dotenv

from transformers import pipeline

from helper import tweet_history, strip_all_entities, clean_hashtags, filter_chars, remove_mult_spaces

load_dotenv()

auth = tweepy.OAuthHandler(getenv('TWITTER_API_KEY'), getenv('TWITTER_API_KEY_SECRET'))
auth.set_access_token(getenv('TWITTER_ACCESS_TOKEN'), getenv('TWITTER_ACCESS_TOKEN_SECRET'))
api = tweepy.API(auth, wait_on_rate_limit=True, parser=tweepy.parsers.JSONParser())

client = tweepy.Client(bearer_token=getenv('TWITTER_BEARER_TOKEN'), access_token=getenv('TWITTER_ACCESS_TOKEN')) 


SENTIMENT_MODEL = "./sentiment_model"
SENTIMENT_TOKENIZER = "./sentiment_tokenizer"

EMOTION_MODEL = "./emotion_model"
EMOTION_TOKENIZER = "./emotion_tokenizer"


sentiment_pipe = pipeline(task="sentiment-analysis", model=SENTIMENT_MODEL, tokenizer=SENTIMENT_TOKENIZER)
emotion_pipe = pipeline(task="sentiment-analysis", model=EMOTION_MODEL, tokenizer=EMOTION_TOKENIZER)


def check_replys(tweet_ID):
    query = f"conversation_id:{tweet_ID} is:reply"
    replys = client.search_recent_tweets(query=query)
    return replys

def clean_text(text):
    return remove_mult_spaces(filter_chars(clean_hashtags(strip_all_entities(emoji.demojize(text)))))

def main(user_name):
    df = tweet_history(user_name, 10, client, api)

    tweets = []
    for tid in df['tweet_id']:
        tid_tweet = check_replys(tid)
        tweet = tid_tweet._asdict()
        tweet['tid'] = tid  # add tid to tweet dictionary
        tweets.append(tweet)

    maybe = []
    for t in tweets:
        if t['data'] != None:
            random = t['data']
            temp_df = pd.DataFrame(random)
            temp_df['original_id'] = t['tid']
            maybe.append(temp_df)

    reduce = pd.concat(maybe, ignore_index=True)
    reduce['id'] = reduce['id'].astype(str)
    reduce['original_id'] = reduce['original_id'].astype(str)

    combined = pd.merge(df, reduce, left_on='tweet_id', right_on='original_id', how='left')
    combined = combined[~combined['id'].isnull()].copy()

    combined['text_cleaned'] = combined['text'].apply(clean_text)
    combined = combined[combined['text_cleaned'] != ''].copy()

    combined['sentiment'] = combined['text_cleaned'].apply(lambda x: sentiment_pipe(x))
    combined['emotion'] = combined['text_cleaned'].apply(lambda x: emotion_pipe(x))

    return combined.to_csv('data.csv', index=False)

if __name__ == '__main__':
    main('0xcarlisle')