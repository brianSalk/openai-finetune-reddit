# openai-finetune-reddit
a group of scripts to automate the fine tuning of an openai language model such as davinci.
## create_jsonl.py
scrapes reddit and formats output to be in the form of jsonl document.  By default scrapes submission titles that end in a questionmark as the prompt and the submission body as the completion.
