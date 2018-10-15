from django.conf import settings

import requests_oauthlib

_cached_twitter_users = {}

class Twitter(object):
	def __init__(self, conference=None):
		if conference:
			token = conference.twitter_token
			secret = conference.twitter_secret
		else:
			token = settings.TWITTER_NEWS_TOKEN
			secret = settings.TWITTER_NEWS_TOKENSECRET

		self.tw = requests_oauthlib.OAuth1Session(settings.TWITTER_CLIENT,
												  settings.TWITTER_CLIENTSECRET,
												  token,
												  secret)


	def post_tweet(self, tweet):
		r = self.tw.post('https://api.twitter.com/1.1/statuses/update.json', data={
			'status': tweet,
		})
		if r.status_code != 200:
			return (False, r.text)
		return (True, None)


class TwitterSetup(object):
	@classmethod
	def get_authorization_data(self):
		oauth = requests_oauthlib.OAuth1Session(settings.TWITTER_CLIENT, settings.TWITTER_CLIENTSECRET)
		fetch_response = oauth.fetch_request_token('https://api.twitter.com/oauth/request_token')
		auth_url = oauth.authorization_url('https://api.twitter.com/oauth/authorize')

		return (auth_url,
				fetch_response.get('oauth_token'),
				fetch_response.get('oauth_token_secret'),
		)

	@classmethod
	def authorize(self, ownerkey, ownersecret, pincode):
		oauth = requests_oauthlib.OAuth1Session(settings.TWITTER_CLIENT,
												settings.TWITTER_CLIENTSECRET,
												resource_owner_key=ownerkey,
												resource_owner_secret=ownersecret,
												verifier=pincode)
		tokens = oauth.fetch_access_token('https://api.twitter.com/oauth/access_token')

		return tokens

