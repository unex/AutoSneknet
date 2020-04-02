from requests import Session
from ratelimit import limits, sleep_and_retry

import logging

log = logging.getLogger('AutoSneknet')

class GremlinsAPI(Session):
    def __init__(self, api_key):
        super().__init__()

        self.API_BASE = "https://gremlins-api.reddit.com"
        self.cookies.set("reddit_session", api_key)

    @sleep_and_retry
    @limits(calls=2, period=1) # 2 calls / second
    def request(self, method, url, **kwargs):
        r = super().request(method, f'{self.API_BASE}{url}', **kwargs)

        log.debug(f'[{self.__class__.__module__}.{self.__class__.__name__}] <{r.status_code}> {method=} {url=} {kwargs}')

        return r

    def room(self):
        return self.get(f'/room')

    def submit_guess(self, _id, csrf) -> bool:
        r = self.post(f'/submit_guess', data = {
            "note_id": _id,
            "csrf_token": csrf
        })

        try:
            r.json()
        except:
            text = r.text.replace('\n', '')
            log.critical(f'[{self.__class__.__module__}.{self.__class__.__name__}] <{r.status_code}> submit_guess {text}')

        return r.json()["result"] == "WIN"
