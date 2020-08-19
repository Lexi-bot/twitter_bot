consumer_key = "SGBOxda2KnbkgR5JAGw9Tvvaq"
consumer_secret = "RzzdOHaNSNjZMB5CwfOGUtyt3t2c7jlod9NqvLECvEhUphn3ks"
access_token = "1295595284701966336-nJtCTgmNawjZDnc6Nd2vtM4gGTTHvO"
access_token_secret = "tb6dHPiK2hSp2dLxRPevd1MNNR7ApVGk3SB3wKflaWvWz"

import tweepy, re

from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt

list_stopwords = []
list_stopwords.extend(stopwords.words('english'))
list_stopwords.extend(stopwords.words('indonesian'))

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API, Cursor

class TwitterClient():
	def __init__(self,twitter_user=None):
		global consumer_key
		global consumer_secret
		global access_token
		global access_token_secret
		self.auth = TwitterAuthenticator(consumer_key,consumer_secret, 
										access_token,access_token_secret).authenticate_twitter_app()
		self.twitter_client = API(self.auth)
		self.twitter_user = twitter_user

	def get_user_timeline_tweets(self, num_tweets):
		tweets = []
		for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user,include_rts=False).items(num_tweets):
			tweets.append(tweet)
		return tweets

	def get_mentions_timeline(self,num_tweets,last_id):
		mention_tweets = []
		for tweet in Cursor(self.twitter_client.mentions_timeline,since_id=last_id).items(num_tweets):
			mention_tweets.append(tweet)
		return mention_tweets

	def reply_media(self,filename,tweet_id):
		self.twitter_client.update_with_media(filename=filename, status=f'@{self.twitter_user} Here is your WordCloud ',in_reply_to_status_id=tweet_id)



class TwitterAuthenticator():

	def __init__(self, consumer_key,consumer_secret, access_token,access_token_secret):
		self.consumer_key = consumer_key
		self.consumer_secret = consumer_secret
		self.access_token = access_token
		self.access_token_secret = access_token_secret

	def authenticate_twitter_app(self):
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)
		return auth

		


class TwitterStreamer():

	def __init__(self):
		global consumer_key
		global consumer_secret
		global access_token
		global access_token_secret
		self.twitter_authenticator = TwitterAuthenticator(consumer_key,consumer_secret,access_token,access_token_secret)

	def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
		listener = TwitterListener(fetched_tweets_filename)
		auth = self.twitter_authenticator.authenticate_twitter_app()
		stream = Stream(auth, listener)
		stream.filter(track=hash_tag_list)
		# api = tweepy.API(auth)	

	# def stream_tweets(self, usernam)


class TwitterListener(StreamListener):

	def __init__(self, fetched_tweets_filename):
		self.fetched_tweets_filename = fetched_tweets_filename

	def on_data(self,data):
		print(data)
		with open(self.fetched_tweets_filename,'a') as tf:
			tf.write(data)
		return True

	def on_error(self,status):
		if status == 420:
			return False
		print(status)
		

if __name__ == '__main__':
	hash_tag_list= ['dame da ne']
	fetched_tweets_filename = 'tweets.txt'


	# WordCloud(stopwords=stop_words, background_color="white", colormap="Dark2",max_font_size=150, random_state=42)

	twitter_client = TwitterClient()	
	# print(len(twitter_client.get_user_timeline_tweets(5000)))
	with open('last_id.txt','r') as f:
		id_txt = f.read().strip()
		if id_txt != '':
			last_id = int(id_txt)
		else:
			last_id = None

	for x in reversed(twitter_client.get_mentions_timeline(100,last_id)):
		tweet = x._json['text']
		tweet_id = x._json['id']
		tweet_id_str = x._json['id_str']

		if tweet.strip().lower() == '@lexikatbot':

			with open('last_id.txt','w+') as f:
				f.write(tweet_id_str)
			
			username = x._json['user']['screen_name']
			new_client = TwitterClient(username)
			all_tweets = []

			for y in new_client.get_user_timeline_tweets(3200):
				norm = re.sub(r'@[^\s]+', '',y._json['text'])
				norm = re.sub(r'https://[^\s]+','',norm)
				norm = re.sub(r'[^\w\s]',' ',norm)
				

				if len(norm) > 0:
					all_tweets.append(norm)
			text = ' '.join(all_tweets)
			print(text)
			wordcloud = WordCloud(stopwords=list_stopwords, collocations=False).generate(text)
			wordcloud.to_file(f'{tweet_id}.png')
			
			new_client.reply_media(f'{tweet_id}.png',tweet_id)
		## reply
		





