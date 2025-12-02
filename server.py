from fastmcp import FastMCP
from xdk import Client
import os

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
    }
    scope="tweet.read tweet.write users.read",
    bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
    client_id=os.getenv("TWITTER_CLIENT_ID"),        # or API Key
    client_secret=os.getenv("TWITTER_CLIENT_SECRET"),
    redirect_uri="https://oauth.pstmn.io/v1/browser-callback"
)

@mcp.tool(name="greet", description="Greet a user by name")
def greet(name: str) -> str:
    return f"Greetings, {name}!"

@mcp.tool(name="get_xdk_version", description="Print XDK version")
def print_xdk_version() -> str:
    return f"XDK version: {xdk.__version__}"

@mcp.tool(name="get_posts_content", description="Get content of posts by ids")
def get_posts_content(ids: str):
    posts = client.posts.get(ids=[ids])
    return posts

@mcp.tool(name="search_recent_tweets", description="Search recent tweets")
def search_recent_tweets(query_params: str):
    if query_params is None:
        query_params = "model context protocol lang:en"
    search_results = client.posts.recent_search(query=query_params)
    return search_results

@mcp.tool(name="post_a_tweet", description="Post a tweet")
def post_a_tweet(tweet: str):
    post = client.posts.create(post_data={"text": tweet})
    return post

if __name__ == "__main__":
    # This runs the server, defaulting to STDIO transport
    mcp.run()
