import praw
import sys
import argparse
import credentials
import re

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
        max_completion_length,max_submissions,
        must_contain, min_rating_for_sub, min_rating_for_comment,
        max_lines,cre_pattern, PROMPT_END=r'\n\n###\n\n',COMP_END="###"):
    if questions_only:
        PROMPT_END = '?'
    comp_regex = re.compile(cre_pattern) if cre_pattern is not None else None
    ans = []
    line_count = 0
    # Loop through subreddits and submissions
    for sub in subreddits.split(' '):
        if line_count == max_lines:
            return "\n".join(ans)
        next_sub = reddit.subreddit(sub)
        sub_count = 0
        for submission in next_sub.top(limit=1_000):
            scraped_current = False
            if sub_count == max_submissions:
                break
            if line_count == max_lines:
                return "\n".join(ans)
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
                and submission.score >= min_rating_for_sub \
                and (comp_regex is None or re.search(comp_regex,selftext) is not None):
                prompt = f'"prompt": "{title}{PROMPT_END}",'
                completion = f'"completion": " {selftext}{COMP_END}"'
                string = '{' + prompt + completion + '}'
                ans.append(string)
                line_count+=1
                scraped_current = True
            # Generate JSON string for comments
            if comments:
                comment_count = 0
                for comment in submission.comments:
                    if line_count == max_lines:
                        return "\n".join(ans)
                    if comment_count >= comments:
                        break
                    try:
                        selftext = comment.body.strip()
                    except Exception:
                        continue
                    selftext = selftext.replace('\n', ' ')
                    selftext = selftext.replace('"', "'")
                    selftext = selftext.replace('\\', '')
                    prompt = f'"prompt": "{title}{PROMPT_END}",'
                    completion = f'"completion": " {selftext}{COMP_END}"'
                    string = '{' + prompt + completion + '}'
                    if len(selftext) <= max_completion_length and \
                    len(selftext) >= min_completion_length and comment.score >= min_rating_for_comment:
                        ans.append(string)
                        scraped_current = True
                        line_count+=1
                        comment_count += 1
            if scraped_current == True:
                sub_count+=1
    return "\n".join(ans)
def input_with_retry(prompt_string, is_valid, err):
    while True:
        print(prompt_string,end="",file=sys.stderr)
        ans = input().strip()
        if is_valid(ans):
            return ans
        print(err,file=sys.stderr)
def input_with_retry_int(prompt_string, is_valid, err, default=0):
    while True:
        print(prompt_string, end="", file=sys.stderr)
        ans = input().strip()
        if is_valid(ans):
            return int(ans) if ans.strip() != "" else default
        print(err,file=sys.stderr)


if __name__ == "__main__":
    # promt user for all the different options
    subreddits = input_with_retry('enter subreddits seperated by spaces: ',
            lambda x: len(x)>0 and re.match(r'^[a-zA-Z\s]*$',x),
            f'please enter a valid space-seperated list of subreddits')
    comments = input_with_retry_int('how many comments per submission[0]? ', 
            lambda x: x.strip().isdigit() or x == '',
            'please enter a valid integer')
    submission_body_yn = input_with_retry('use submission body as completion? (Y/n) ',
            lambda x: x.strip().lower() in ['y','n',''],
            "please enter 'y' or 'n'")
    submission_body = submission_body_yn.strip().lower() != 'n'

    questions_only =input_with_retry('only use questions as prompts? (y/N)',
            lambda x: x.strip().lower() in ['y', 'n',''],
            "please enter 'y' or 'n'")
    questions_only = questions_only != 'n'
    min_completion_length = input_with_retry_int('minimum length before completions are considered [0] ',
            lambda x: (x.isdigit() and int(x) >= 0) or x == '',
            'please enter a non-negative integer')
    max_completion_length = input_with_retry_int('maximum length before completions are ignored [200] ',
            lambda x: (x.isdigit() and int(x) > min_completion_length)  or (x == '' and min_completion_length < 200),
            f'please enter a non-negative integer greater than min completion length of {min_completion_length}',
            200)
    submissions_per_sub = input_with_retry_int('number of submissions per subreddit [1,000]: ',
            lambda x: (x.isdigit() and int(x)>0) or x.strip() == "",
            'please enter a positive integer',
            default=1_000)
    min_rating_for_sub = input_with_retry_int('minimum rating for submission [-inf]: ',
            lambda x: x.strip().isdigit() or x.strip() == '',
            'please enter an integer', 
            -float('inf'))
    min_rating_for_comment = 0
    if comments > 0:
        min_rating_for_comment = input_with_retry_int('minimum rating for comments [-inf]: ',
                lambda x: x.isdigit() or x.strip() == '',
                'please enter a valid digit',
                -float('inf'))
    max_lines = input_with_retry_int('max number of prompt/completion pairs [inf]: ',
            lambda x: x.isdigit() or x.strip() == '', 
            'please enter a positive integer',
            float('inf'))
    comp_regex = input_with_retry('completion regex [.*]: ',
            lambda x: True,
            'SHOULD NOT DISPLAY')
    if comp_regex == "":
        comp_regex = None
    prompt_end = input_with_retry(r'prompt end [\n\n###\n\n]', lambda x: True,
    '')
    comp_end = input_with_retry(r'completion end [\n\n###\n\n]', lambda x: True,'')

    
     
    jsonl = create(subreddits,comments,submission_body,
        questions_only,min_completion_length,
        max_completion_length,submissions_per_sub,
        "NOT SUPPORTED", min_rating_for_sub, min_rating_for_comment,
        max_lines, comp_regex, prompt_end, comp_end)
    print(jsonl)
