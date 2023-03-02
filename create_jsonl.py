import praw
import sys
import argparse
import credentials

# Create Reddit instance
reddit = praw.Reddit(
    client_secret=credentials.client_secret,
    client_id=credentials.client_id,
    usename=credentials.usename,
    password=credentials.password,
    user_agent=credentials.user_agent
)

# Set up argparse
parser = argparse.ArgumentParser()
parser.add_argument('--prompt-end', default='', help='only use submission titles that end with PROMPT_END')
parser.add_argument('--comments', type=int, help='use first-level comments as completions')
parser.add_argument('-s', '--subreddits', required=True, help='requires a + separated list of subreddits')
parser.add_argument('--questions-only', action='store_true', help='only scrape prompts that end in a question mark')
args = parser.parse_args()

PROMPT_END = '\n\n###\n\n'
COMP_END = '.#,'
if args.questions_only:
    PROMPT_END = '?'

# Loop through subreddits and submissions
for sub in args.subreddits.split('+'):
    next_sub = reddit.subreddit(sub)
    for submission in next_sub.top(limit=1000):
        title = submission.title.strip()
        selftext = submission.selftext.strip()

        # Skip if title does not end with question mark
        if args.questions_only and not title.endswith('?'):
            continue

        # Remove question mark from title
        if args.questions_only:
            title = title[:-1]

        # Replace special characters
        title = title.replace('"', "'")
        title = title.replace("\\", '')
        selftext = selftext.replace('\n', ' ')
        selftext = selftext.replace('"', "'")
        selftext = selftext.replace("\\", '')

        # Generate JSON string
        if selftext:
            prompt = f'"prompt": "{title}{PROMPT_END}",'
            completion = f'"completion": " {selftext}{COMP_END}"'
            string = '{' + prompt + completion + '}'
            print(string)

        # Generate JSON string for comments if args.comments specified
        if args.comments:
            comment_count = 0
            for comment in submission.comments:
                if comment_count > args.comments:
                    break
                try:
                    selftext = comment.body.strip()
                except Exception:
                    break
                selftext = selftext.replace('\n', ' ')
                selftext = selftext.replace('"', "'")
                selftext = selftext.replace('\\', '')
                prompt = f'"prompt": "{title}{PROMPT_END}",'
                completion = f'"completion": " {selftext}{COMP_END}"'
                string = '{' + prompt + completion + '}'
                print(string)
                comment_count += 1

