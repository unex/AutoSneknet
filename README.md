# AutoSneknet

Developed on Python v3.8.1 use other versions at your own risk

Move `.env.example` to `.env` and put your shit in there

`REDDIT_TOKEN` can be found as `reddit_session` under Cookies in your browsers dev tools while visiting https://reddit.com

```bash
pipenv install
pipenv run python main.py
```

"Set-it-and-forget-it" example

```bash
while true; git pull; do pipenv run python main.py; sleep 10; done
```
