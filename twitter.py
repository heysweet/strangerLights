import random
from io import BytesIO

import requests
import tweepy

from secrets import *

auth = tweepy.OAuthHandler(consumer_key, consumer_secret) # Twitter requires all requests to use OAuth for authentication
auth.set_access_token(access_token, access_secret) 
api = tweepy.API(auth)

username = '@halloweenwall'
validChars = set(' abcdefghijklmnopqrstuvwxyz')

# create a class inheriting from the tweepy StreamListener
class BotStreamer(tweepy.StreamListener):
  # Called when a new status arrives which is passed down from the on_data method of the StreamListener
  def on_status(self, status):
    text = status.text
    text = text.lower()
    text = text.replace(username, '').strip()
    text = ''.join([c for c in text if c in validChars])
    api.send_direct_message(
      self.logging_username,
      text=status.text + ' from ' + status.user.screen_name
    )
    self.onTweet(self.strip, text, api)

def setupStream(strip, on_tweet, logging_username):    
  myStreamListener = BotStreamer()
  myStreamListener.strip = strip
  myStreamListener.onTweet = on_tweet
  myStreamListener.logging_username = logging_username

  # Construct the Stream instance
  stream = tweepy.Stream(auth, myStreamListener)
  stream.filter(track=[username])
  return stream

def log(x):
  print(x)

if __name__ == '__main__':
  setupStream(log)