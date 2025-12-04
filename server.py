from fastmcp import FastMCP
from xdk.client import Client
import os
from typing import List, Dict, Any  # For type hints
import xdk
from xdk.posts.models import CreateRequest
from xdk.oauth2_auth import OAuth2PKCEAuth
#from urllib.parse import urlparse
# Create a basic server instance
mcp = FastMCP(name="TwitterMCPServer")

# Initialize the client
client = Client(
    token={
        "oauth_token": os.getenv("TWITTER_ACCESS_TOKEN"),           # this is the access_token
        "oauth_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        "consumer_key": os.getenv("TWITTER_API_KEY"),
        "consumer_secret": os.getenv("TWITTER_API_SECRET"),
        "access_token": os.getenv("TWITTER_ACCESS_TOKEN_SECRET")       
    },
    scope="tweet.read tweet.write users.read offline.access",
    bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
    client_id=os.getenv("TWITTER_CLIENT_ID"),        # or API Key
    client_secret=os.getenv("TWITTER_CLIENT_SECRET"),
    redirect_uri="https://oauth.pstmn.io/v1/browser-callback"
)

auth = OAuth2PKCEAuth(
    base_url="https://x.com/i",
    client_id=os.getenv("TWITTER_CLIENT_ID"),
    redirect_uri="https://oauth.pstmn.io/v1/browser-callback",
    scope= "tweet.read tweet.write users.read offline.access"
)

@mcp.tool(name="greet", description="Greet a user by name")
def greet(name: str) -> str:
    return f"Greetings, {name}!"

@mcp.tool(name="get_xdk_version", description="Print XDK version")
def print_xdk_version() -> str:
    return f"XDK version: {xdk.__version__}"

@mcp.tool(name="get_auth_url", description="Get auth URL")
def get_auth_url() -> str:
    auth_url, state = auth.get_authorization_url()
    return f"Visit this URL to authorize: {auth_url}"

@mcp.tool(name="fetch_auth_token", description="Fetch auth token")
def fetch_auth_token(code: str) -> str:
    global client
    tokens = auth.fetch_token(authorization_response=code)
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]  # Store for renewal
    client = Client(
        token={
            "oauth_token": os.getenv("TWITTER_ACCESS_TOKEN"),           # this is the access_token
            "oauth_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
            "consumer_key": os.getenv("TWITTER_API_KEY"),
            "consumer_secret": os.getenv("TWITTER_API_SECRET"),
            "access_token": access_token, #os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
            "token_type": "Bearer"
        },
        scope="tweet.read tweet.write users.read offline.access",
        bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
        client_id=os.getenv("TWITTER_CLIENT_ID"),        # or API Key
        client_secret=os.getenv("TWITTER_CLIENT_SECRET"),
        redirect_uri="https://oauth.pstmn.io/v1/browser-callback"
    )
    #client = Client(oauth2_access_token=access_token)
    return f"Tokens: access {access_token} refresh {refresh_token}"

@mcp.tool(name="get_tweet_content", description="Get content of posts by ids")
def get_tweet_content(id: str):
    posts = client.posts.get_by_id(id=id)
    return posts

@mcp.tool(name="search_recent_tweets", description="Search recent tweets")
def search_recent_tweets(query_params: str):
    if query_params is None:
        query_params = "model context protocol lang:en"
    search_results = client.posts.search_recent(query=query_params)
    return search_results

@mcp.tool(name="post_a_tweet", description="Post a tweet")
def post_a_tweet(tweet: str):
    request = CreateRequest(
        text=tweet
    )
    post = client.posts.create(body=request)
    return post

if __name__ == "__main__":
    # This runs the server, defaulting to STDIO transport
    mcp.run()
