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

def create(subreddits,comments,submission_body,
        questions_only,min_completion_length,
        max_completion_length,submissions_per_sub,
        must_contain, min_rating_for_sub, min_rating_for_comment):
    PROMPT_END = '\n\n###\n\n'
    COMP_END = '.#,'
    if questions_only:
        PROMPT_END = '?'

    ans = []
    # Loop through subreddits and submissions
    for sub in subreddits.split(' '):
        next_sub = reddit.subreddit(sub)
        for submission in next_sub.top(limit=submissions_per_sub):
            title = submission.title.strip()
            selftext = submission.selftext.strip()

            # Skip if title does not end with question mark
            if questions_only and not title.endswith('?'):
                continue

            # Remove question mark from title
            if questions_only:
                title = title[:-1]
            # Replace special characters
            title = title.replace('"', "'")
            title = title.replace("\\", '')
            selftext = selftext.replace('\n', ' ')
            selftext = selftext.replace('"', "'")
            selftext = selftext.replace("\\", '')

            # Generate JSON string using submission body
            if selftext and submission_body and submission and len(selftext) >= min_completion_length and len(selftext) <= max_completion_length \
                and submission.score >= min_rating_for_sub:
                prompt = f'"prompt": "{title}{PROMPT_END}",'
                completion = f'"completion": " {selftext}{COMP_END}"'
                string = '{' + prompt + completion + '}'
                ans.append(string)
            # Generate JSON string for comments
            if comments:
                comment_count = 0
                for comment in submission.comments:
                    if comment_count >= comments:
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
                    if len(selftext) <= max_completion_length and \
                    len(selftext) >= min_completion_length and comment.score >= min_rating_for_comment:
                        ans.append(string)
                        comment_count += 1
    return "\n".join(ans)

if __name__ == "__main__":
	# Set up argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('--prompt-end', default='', help='only use submission titles that end with PROMPT_END')
	parser.add_argument('--comments', type=int,default=0, help='use first-level comments as completions')
	parser.add_argument('-s', '--subreddits', required=True, help='requires a + separated list of subreddits')
	parser.add_argument('--questions-only', action='store_true', help='only scrape prompts that end in a question mark')
	parser.add_argument('--submission_body', action='store_true',help='include the submission body as completion')
	parser.add_argument('--min_completion_length',type=int, help='set mininum length of a completion')
	parser.add_argument('--max_completion_length',type=int, help='set maximum completion length')
	parser.add_argument('--submissions_per_sub',type=int,default=1_000, help='number of submissions per subreddit to scrape')
	parser.add_argument('--min_rating_for_sub', type=int, default=0,help='minimum number of upvotes for submission to be considered for jsonl')
	parser.add_argument('--min_rating_for_comment', type=int, default=0, help='min number of upvotes for comment to be considered for jsonl')
	args = parser.parse_args()
	create(args.subreddits,args.comments,args.submission_body,
        args.questions_only,args.min_completion_length,
        args.max_completion_length,args.submissions_per_sub,
        "NOT SUPPORTED", args.min_rating_for_sub, args.min_rating_for_comment)
