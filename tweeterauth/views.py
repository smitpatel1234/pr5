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
    oauth_verifier = request.GET.get("oauth_verifier")

    if not oauth_verifier:
        return HttpResponse("❌ Missing oauth_verifier. Login again.")

    # Retrieve request token from session
    request_token = request.session.get("request_token")

    if not request_token:
        return HttpResponse("❌ Missing request_token. Please restart login.")

    auth = tweepy.OAuth1UserHandler(
        settings.TWITTER_API_KEY,
        settings.TWITTER_API_SECRET,
    )

    # Must reassign stored request_token
    auth.request_token = request_token

    try:
        access_token, access_token_secret = auth.get_access_token(oauth_verifier)

        # Save final tokens (for API usage later)
        request.session["access_token"] = access_token
        request.session["access_token_secret"] = access_token_secret

        api = tweepy.API(auth)
        user = api.verify_credentials()

        return render(request, "twitter_profile.html", {"user": user._json})
    except Exception as e:
        return HttpResponse(f"Callback error: {e}")

