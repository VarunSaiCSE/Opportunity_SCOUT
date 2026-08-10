import feedparser

url = "https://www.reddit.com/r/SaaS/top/.rss?t=day"
feed = feedparser.parse(url)
print(f"Status: {feed.get('status')}")
print(f"Entries: {len(feed.entries)}")
if len(feed.entries) > 0:
    print(f"First title: {feed.entries[0].title}")

