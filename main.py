import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import asyncpraw
import asyncio
import datetime as dt
import pandas as pd

nltk.download('vader_lexicon')
nltk.download('stopwords')


# In[3]:


reddit = praw.Reddit(client_id='*********',
                    client_secret='******************',
                    user_agent='*********') ## to use this, make a Reddit app. Client ID is in top left corner, client secret is given, and user agent is the username that the app is under

sub_reddits = reddit.subreddit('wallstreetbets')
stocks = ["AMZN", "GOOG", "MSFT", "CRWD"]
# For example purposes. To use this as a live trading tool, you'd want to populate this with tickers that have been mentioned on the pertinent community (WSB in our case) in a specified period.

def get_date(date):
    return dt.datetime.fromtimestamp(date)

async def commentSentiment(submission):
    await submission.load()
    await submission.comments.replace_more(limit=0)
    comments = submission.comments.list()
    
    bodyComment = [comment.body for comment in comments if hasattr(comment, 'body')]
    sia = SIA()
    
    results = []
    for line in bodyComment:
        scores = sia.polarity_scores(line)
        scores['headline'] = line
        results.append(scores)

    if not results:
        return 0

    df = pd.DataFrame.from_records(results)
    df['label'] = 0
    df.loc[df['compound'] > 0.1, 'label'] = 1
    df.loc[df['compound'] < -0.1, 'label'] = -1
    
    averageScore = df['label'].mean()
    return averageScore

async def latestComment(submission):
    await submission.load()
    await submission.comments.replace_more(limit=0)
    comments = submission.comments.list()
    
    if not comments:
        return 0

    dates = [comment.created_utc for comment in comments if hasattr(comment, 'created_utc')]
    return max(dates) if dates else 0

async def main():
    submission_statistics = []

    for ticker in stocks:
        subreddit = await reddit.subreddit("wallstreetbets")
        print(f"Searching for {ticker}...")
        count = 0
        async for submission in subreddit.search(ticker, limit=200):
            count += 1
            await submission.load()
            if submission.domain != "self.wallstreetbets":
                continue
            
            print(f"Found submission {count} for {ticker}...")
            
            sentiment = await commentSentiment(submission)
            if sentiment == 0:
                continue
            print(f"Loaded comments of submission {count} for {ticker}...")
            latest_comment = await latestComment(submission)

            d = {
                'ticker': ticker,
                'num_comments': submission.num_comments,
                'comment_sentiment_average': sentiment,
                'latest_comment_date': latest_comment,
                'score': submission.score,
                'upvote_ratio': submission.upvote_ratio,
                'date': submission.created_utc,
                'domain': submission.domain,
                'num_crossposts': submission.num_crossposts,
                'author': str(submission.author)
            }

            submission_statistics.append(d)
        print(f"Found {count} submissions for {ticker}")

    df = pd.DataFrame(submission_statistics)

    df["timestamp"] = df["date"].apply(get_date)
    df["commentdate"] = df["latest_comment_date"].apply(get_date)
    df.sort_values("latest_comment_date", inplace=True)

    df.to_csv('Reddit_Sentiment_Equity2.csv', index=False) 
    
    print(df.head())

loop = asyncio.get_event_loop()

if loop.is_running():
    # For environments like Spyder or Jupyter
    task = loop.create_task(main())
else:
    loop.run_until_complete(main())
