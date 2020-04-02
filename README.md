# AutoSneknet

Developed on Python v3.8.1 use other versions at your own risk

Move `.env.example` to `.env` and put your shit in there

`REDDIT_TOKEN` can be found as `reddit_session` under Cookies in your browsers dev tools while visiting https://reddit.com

## Standard Install

```bash
pipenv install
pipenv run python main.py
```

## Experimental GPT-2 Matching

Borrowed from [gpt-2-output-dataset](https://github.com/openai/gpt-2-output-dataset/tree/master/detector)

```https://storage.googleapis.com/gpt-2/detector-models/v1/detector-large.pt```

or

```wget https://storage.googleapis.com/gpt-2/detector-models/v1/detector-base.pt```

or find another one idk let me know how it goes

```bash
pipenv install --dev
pipenv run python main.py
```

## "Set-it-and-forget-it" example

```bash
while true; git pull; do pipenv run python main.py; sleep 10; done
```
