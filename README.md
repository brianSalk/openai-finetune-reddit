# openai-finetune-reddit
a group of scripts to automate the fine tuning of an openai language model such as davinci.
## create_jsonl_from_reddit.py
scrapes reddit and formats output to be in the form of jsonl document.  By default scrapes submission titles that end in a questionmark as the prompt and the submission body as the completion.  
Can optionally scrape the first n comments of a submission, depending on the command line arguments provided. 

# How To Use
Unfortunatly you need to create a reddit app in order to use the `create_jsonl_from_reddit.py` script.  Fortunatly creating a reddit app is very straight forward.  
Once you are logged into your reddit account, visit [this website](https://www.reddit.com/prefs/apps/) to create your app.  
The whole reason you create the app is to obtain your `client_id` and `client_secret`  [this image](https://imgur.com/a/JqxNOvf) shows where to find those.    
Once you get that information, create a file called `credentials.py` and fill the file with the following text replacing text in the `<angle brackets>` with your own information.  
```
client_secret=<client_secret> # located after word "secret"
client_id=<client_id> # located right under app name
usename=<your_reddit_username> # your reddit user name
password="<your reddit password>" # your reddit password
user_agent="blahblah/readonlyadfasdf" # set equal to any string, this string should work fine
```
