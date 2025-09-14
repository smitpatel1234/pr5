from django.shortcuts import render

# Create your views here.
import tweepy
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponse

def twitter_login(request):
    auth = tweepy.OAuth1UserHandler(
        settings.TWITTER_API_KEY,
        settings.TWITTER_API_SECRET,
        settings.TWITTER_CALLBACK_URL
    )
    try:
        redirect_url = auth.get_authorization_url()
        request.session['request_token'] = auth.request_token
        return redirect(redirect_url)
    except Exception as e:
        return HttpResponse(f"Error: {e}")

def twitter_callback(request):
    request_token = request.session.pop('request_token', None)
    verifier = request.GET.get('oauth_verifier')

    auth = tweepy.OAuth1UserHandler(
        settings.TWITTER_API_KEY,
        settings.TWITTER_API_SECRET
    )
    auth.request_token = request_token

    try:
        auth.get_access_token(verifier)
        api = tweepy.API(auth)

        # ✅ Get user profile
        user = api.verify_credentials()
        return render(request, "twitter_profile.html", {"user": user})

    except Exception as e:
        return HttpResponse(f"Callback Error: {e}")
