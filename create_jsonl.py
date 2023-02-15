import praw
import sys
import argparse
import credentials
reddit = praw.Reddit(
    client_secret=credentials.client_secret, # located after word "secret"
    client_id=credentials.client_id, # located right under app name
    usename=credentials.usename, # your reddit user name
    password=credentials.password, # your reddit password
    user_agent=credentials.user_agent # set equal to any string
    )
# start argparse stuff
parser = argparse.ArgumentParser()
parser.add_argument('--prompt-end', default='', help='only use submission titles that end with PROMPT_END')
parser.add_argument('--comments', type=int, help='use first-level comments as completions')
parser.add_argument('-s','--subreddits', required=True, )
args = parser.parse_args()
# end   argparse stuff
for sub in args.subreddits.split('+'):
    next_sub = reddit.subreddit(sub)
    for submission in next_sub.top(limit=1_000):
        if submission.title.endswith('?'):
            title = submission.title.strip()
            title = title.replace('"', "'")
            title = title.replace('?','')
            title = title.replace("\\",'')
            selftext = submission.selftext.strip()
            selftext = selftext.replace('\n',' ')
            selftext = selftext.replace('"', "'")
            selftext = selftext.replace("\\",'')
            if selftext:
                string = f'"prompt": "{title}?", "completion": " {selftext},#."'
                string = '{' + string +  '}'
                print(string)
            if args.comments:
                comment_count = 0
                for comment in submission.comments:
                    if comment_count > args.comments:
                        break
                    try:
                        selftext = comment.body.strip()
                    except Exception:
                        break
                    selftext = selftext.replace('\n',' ')
                    selftext = selftext.replace('"', "'")
                    selftext = selftext.replace('\\','')
                    string = f'"prompt": "{title}?", "completion": " {selftext},#."'
                    string = '{' + string +  '}'
                    print(string)
                    comment_count += 1
