import tweepy

API_KEY = ""
API_SECRET = ""


def get_twitter_profile(access_token: str, access_token_secret: str) -> dict:
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    user = api.get_user()
    return {
        "name": user.name,
        "username": user.screen_name,
        "image": user.profile_image_url_https,
    }

