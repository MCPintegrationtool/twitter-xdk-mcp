from fastmcp import FastMCP
from xdk.client import Client
import os
from typing import List, Dict, Any  # For type hints
import xdk
from xdk.posts.models import CreateRequest
from xdk.oauth2_auth import OAuth2PKCEAuth
import base64
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
    client_secret=os.getenv("TWITTER_CLIENT_SECRET"),
    redirect_uri="https://oauth.pstmn.io/v1/browser-callback",
    scope= "tweet.read tweet.write users.read offline.access",
    token={
        "access_token": os.getenv("TWITTER_ACCESS_TOKEN_SECRET")       
    }    
)

@mcp.tool(name="greet", description="Greet a user by name")
def greet(name: str) -> str:
    return f"Greetings, {name}!"

@mcp.tool(name="get_xdk_version", description="Print XDK version")
def print_xdk_version() -> str:
    return f"XDK version: {xdk.__version__}"

@mcp.tool(name="get_auth_url", description="Get auth URL")
def get_auth_url() -> str:
    global auth
    auth_url, state = auth.get_authorization_url()
    return f"Visit this URL to authorize: {auth_url}"

@mcp.tool(name="fetch_auth_token", description="Fetch auth token")
def fetch_auth_token(url: str) -> str: # url/code
    global client, auth
    auth.base_url = "https://api.x.com"
    tokens = auth.fetch_token(authorization_response=url)
    # try:
    #     tokens = auth.fetch_token(authorization_response=url)
    # except Exception as e:
    #     return f"Auth token retrieve failed: {str(e)}"
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

@mcp.tool(name="custom_auth_token", description="Custom auth token")
def custom_auth_token(authorization_response: str) -> Dict[str, Any]:
    global auth
    auth.base_url = "https://api.x.com"
    # build basic auth header
    ids = f"{os.getenv('TWITTER_CLIENT_ID')}:{os.getenv('TWITTER_CLIENT_SECRET')}"
    basic = base64.b64encode(ids.encode()).decode()
    token = auth.oauth2_session.fetch_token(
        token_url=f"{auth.base_url}/2/oauth2/token",
        authorization_response=authorization_response,
        code_verifier=auth.code_verifier,
        # DO NOT pass include_client_id=True for confidential clients
        client_id=os.getenv('TWITTER_CLIENT_ID'),
        client_secret=os.getenv("TWITTER_CLIENT_SECRET"),
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
    )
    return token

@mcp.tool(name="print_oauth_session", description="Print OAuth Session")
def print_oauth_session():
    return str(auth.oauth2_session)

@mcp.tool(name="get_base_url", description="Get base URL")
def get_base_url() -> str:
    global auth
    return auth.base_url

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
