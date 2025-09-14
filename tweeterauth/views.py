from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import tweepy
from asgiref.sync import sync_to_async


# Setup Twitter client (Bearer Token from settings.py)
client = tweepy.Client(bearer_token=settings.TWITTER_BEARER_TOKEN)


# ---------- PUBLIC PROFILE ----------
async def twitter_profile_api(request, username):
    try:
        # Run Tweepy in thread-safe way
        user = await sync_to_async(client.get_user)(
            username=username,
            user_fields=["profile_image_url", "public_metrics", "description", "created_at"]
        )

        if not user.data:
            return JsonResponse({"error": "User not found"}, status=404)

        profile = {
            "id": user.data.id,
            "username": user.data.username,
            "name": user.data.name,
            "description": user.data.description,
            "profile_image_url": user.data.profile_image_url,
            "public_metrics": user.data.public_metrics,
            "created_at": user.data.created_at
        }

        # Get tweets safely
        tweets_data = await sync_to_async(client.get_users_tweets)(
            id=user.data.id,
            tweet_fields=["created_at", "public_metrics"],
            max_results=5
        )

        tweets = []
        if tweets_data.data:
            for t in tweets_data.data:
                tweets.append({
                    "id": t.id,
                    "text": t.text,
                    "created_at": t.created_at,
                    "public_metrics": t.public_metrics
                })

        if request.headers.get("Accept") == "application/json":
            return JsonResponse({"profile": profile, "tweets": tweets})

        return render(request, "public_twitter.html", {"profile": profile, "tweets": tweets})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ---------- LOGIN ----------
async def twitter_login(request):
    auth = tweepy.OAuth1UserHandler(
        settings.TWITTER_API_KEY,
        settings.TWITTER_API_SECRET,
        settings.TWITTER_CALLBACK_URL
    )
    try:
        # Run Tweepy call safely
        redirect_url = await sync_to_async(auth.get_authorization_url)()
        request.session['request_token'] = auth.request_token
        return redirect(redirect_url)
    except Exception as e:
        return HttpResponse(f"Error: {e}")


# ---------- CALLBACK ----------
def twitter_callback(request):
    oauth_verifier = request.GET.get("oauth_verifier")

    if not oauth_verifier:
        return HttpResponse("❌ Missing oauth_verifier. Login again.")

    request_token = request.session.get("request_token")
    if not request_token:
        return HttpResponse("❌ Missing request_token. Please restart login.")

    auth = tweepy.OAuth1UserHandler(
        settings.TWITTER_API_KEY,
        settings.TWITTER_API_SECRET,
    )
    auth.request_token = request_token

    try:
        access_token, access_token_secret = auth.get_access_token(oauth_verifier)
        request.session["access_token"] = access_token
        request.session["access_token_secret"] = access_token_secret

        api = tweepy.API(auth)
        user = api.verify_credentials()

        return render(request, "twitter_profile.html", {"user": user._json})
    except Exception as e:
        return HttpResponse(f"Callback error: {e}")
