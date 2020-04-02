from typing import List
import requests
from requests import Session

import logging

log = logging.getLogger('AutoSneknet')
class SneknetAuthException(requests.exceptions.HTTPError):
    pass

class Sneknet(Session):
    def __init__(self, token):
        super().__init__()
        self.headers.update({'Authorization': f'{token}', 'User-Agent': 'AutoSneknet'})
        self.API_BASE = "https://api.snakeroom.org/y20"

    def request(self, method, url, **kwargs):
        r = super().request(method, f'{self.API_BASE}{url}', **kwargs)

        log.debug(f'[{self.__class__.__module__}.{self.__class__.__name__}] <{r.status_code}> {method=} {url=} {kwargs}')

        try:
            d = r.json()
            if d.get('error'):
                raise SneknetAuthException(d.get('error'))
        except:
            logging.critical(f'[{self.__class__.__module__}.{self.__class__.__name__}] {url=} {r.text}')

        return r

    def submit(self, options) -> list:
        r = self.post('/submit', json={
            "options": options
        })
        return list(r.json()['seen'].values())[0]['seen']

    def query(self, messages: List[str]) -> dict:
        r = self.post('/query', json={"options": messages})
        return {d['i']: d['correct'] for d in r.json()['answers']}
