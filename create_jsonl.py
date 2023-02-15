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
parser.add_argument('-s','--subreddits', required=True, help='requires a + seperated list of subreddits')
parser.add_argument('--questions-only',action='store_true', help='only scrape propmpts that end in a questionmark')
args = parser.parse_args()
# end   argparse stuff
PROMPT_END='\n\n###\n\n'
COMP_END='.#,'
if args.questions_only:
    PROMPT_END = '?'
for sub in args.subreddits.split('+'):
    next_sub = reddit.subreddit(sub)
    for submission in next_sub.top(limit=1_000):
        selftext = submission.selftext
        title = submission.title.strip()
        if args.questions_only and not title.endswith('?'):
            continue
        if args.questions_only:
            title = title.replace('?','') # remove PROMPT_END
        title = title.replace('"', "'") # convert " to '
        title = title.replace("\\",'') # remove escape chars
        selftext = selftext.replace('\n',' ') # remove newlines in completion
        selftext = selftext.replace('"', "'")
        selftext = selftext.replace("\\",'')
        selftext = submission.selftext.strip()
        if selftext:
            string = f'"prompt": "{title}{PROMPT_END}", "completion": " {selftext}{COMP_END}"'
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
                string = f'"prompt": "{title}{PROMPT_END}", "completion": " {selftext}{COMP_END}"'
                string = '{' + string +  '}'
                print(string)
                comment_count += 1
