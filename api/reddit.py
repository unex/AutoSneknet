from requests import Session

class Reddit(Session):
    def __init__(self, api_key):
        super().__init__()

        self.cookies.set("reddit_session", api_key)
        self.headers.update({'User-Agent': 'AutoSneknet'})

    def me(self):
        r = self.get('https://www.reddit.com/user/me/about.json')

        user = r.json()
        if isinstance(user, dict):
            return user['data']
        else:
            return None
