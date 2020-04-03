import os
import sys
import re
import time
import random

from colored import fore, back, style

from api import GremlinsAPI, Sneknet, Reddit
from logger import log


REDDIT_TOKEN = os.environ.get("REDDIT_TOKEN", None)
if not REDDIT_TOKEN:
    print(back.RED + fore.BLACK)
    print('\n\nYOU MUST SET "REDDIT_TOKEN"\n\n')
    print(style.RESET, end='')
    sys.exit(0)

SNEKNET_TOKEN = os.environ.get("SNEKNET_TOKEN", None)

re_csrf = re.compile(r"<gremlin-app\n\s*csrf=\"(.*)\"")
re_notes_ids = re.compile(r"<gremlin-note id=\"(.*)\"")
re_notes = re.compile(r"<gremlin-note id=\".*\">\n\s*(.*)")
re_plswait = re.compile(r"<gremlin-prompt>\n.*<h1>(.*)</h1>\n.*<p>Please try again in a moment.</p>")

sneknet = Sneknet(SNEKNET_TOKEN)
gremlins = GremlinsAPI(REDDIT_TOKEN)
reddit = Reddit(REDDIT_TOKEN)

print(fore.GREEN_YELLOW)
print('🐍  https://snakeroom.org/sneknet 🐍')
print(style.RESET)

user = reddit.me()

if not user:
    raise Exception(f'Could not fetch user, check your REDDIT_TOKEN')

REPORT = False
if '--report' in sys.argv:
    print('Report exploit enabled')
    REPORT = True

try:
    from gpt2 import Roberta
    print("Initalizing GPT-2...", end='\r')
    roberta = Roberta()
    print('GPT-2 Model Initialized')
except:
    roberta = None

def styled_percent(num):
    # idk what to make these values
    color = fore.RED
    if num >= .75: color = fore.YELLOW
    if num >= .9: color = fore.GREEN

    return f'{color}{num*100:.1f}%{style.RESET}'

def cool_algo_name(notes):
    if roberta:
        datas = {k: roberta.query(v)[0] for k, v in notes.items()}
        val = max(datas.values())
        _id = list(datas.keys())[list(datas.values()).index(val)]
        log.debug(f'GPT2 {val} "{notes[_id]}" {datas=} {notes=}')

        if val >= .8:
            print(f'[{fore.ORANGE_1} GPT  {(val)*100:2.0f}% {style.RESET}][{len(notes)}]', end='')
            return _id

    if REPORT:
        return None

    longest = max(notes.values(), key=len)
    _id = list(notes.keys())[list(notes.values()).index(longest)]
    log.debug(f'Selected longest {longest}, {_id=} from {notes.values()=}')
    print(f'[{fore.YELLOW}   LONG   {style.RESET}][{len(notes)}]', end='')

    return _id

status = gremlins.status()

session_games_played: int = 0
session_games_won: int = 0

total_games_played: int = status['games_played']
total_games_won: int = status['games_won']

win_streak = 0

while True:
    log.debug('='*50)
    room = gremlins.room()

    plswait = re_plswait.findall(room.text)
    if plswait:
        for i in range(6):
            print(f'{back.WHITE}{fore.BLACK}{plswait[0]}{back.BLACK if i % 2 == 0 else back.WHITE} {style.RESET}', end='\r')
            time.sleep(1)
        continue

    print('', end='')

    csrf = re_csrf.findall(room.text)[0]
    ids = re_notes_ids.findall(room.text)
    notes_content = re_notes.findall(room.text)

    notes = {ids[i]: notes_content[i] for i in range(len(ids))}

    # Query Sneknet for known, and remove known humans from the notes
    known = sneknet.query(notes_content)
    if True in known.values():
        print(f'[{fore.CYAN} IMPOSTER {style.RESET}][{fore.GREEN_YELLOW}S{style.RESET}]', end='')
        # Sneknet doesnt return a full dict and it FUCKS my shit
        vals = [known.get(k, False) for k in range(5)]
        _id = ids[vals.index(True)]
        log.debug(f'Confirmed imposter from Sneknet {known=} {_id=} "{notes[_id]}"')

    else:
        if len(known) == 5:
            log.error(f'Zero length notes?!?!?! {notes=} {known=}')
            _id = cool_algo_name(notes)

        else:
            for i, v in known.items():
                del notes[ids[i]]
                log.debug(f'Dropped known human from notes {ids[i]=}')

            if not notes:
                log.warning('All 5 notes were confirmed human ¯\_(ツ)_/¯')
                continue

            if len(notes) == 1:
                print(f'[{fore.CYAN} IMPOSTER {style.RESET}][D]', end='')
                _id = list(notes.keys())[0]
                log.debug(f'Confirmed imposter from last note {_id=} "{notes[_id]}"')

            else:
                _id = cool_algo_name(notes)

    if not _id:
        print(f'[{fore.YELLOW}  REPORT  {style.RESET}][{len(notes)}]', end='\n')
        gremlins.report(ids[0], csrf)
        log.debug(f'Reported {ids[0]}, {ids=} from {notes.values()=}')
        continue

    text = notes[_id]

    print(f'[ {text:110} ]', end='')

    is_correct = gremlins.submit_guess(_id, csrf)

    log.debug(f'{is_correct=}')

    if is_correct:
        print(f'[{fore.LIGHT_GREEN} W {style.RESET}]', end='')
        session_games_won += 1
        total_games_won += 1
        win_streak += 1
    else:
        print(f'[{fore.RED} L {style.RESET}]', end='')
        win_streak = 0

    session_games_played += 1
    total_games_played += 1

    if len(notes) == 2:
        log.debug(f'50% chance "{notes[_id]}" {is_correct=}')
        del notes[_id] # delete the one we know
        options = [
            {
                "message": text,
                "correct": is_correct
            },
            {
                "message": notes[list(notes.keys())[0]],
                "correct": not is_correct
            }
        ]

    else:
        options = [
            {
                "message": text,
                "correct": True
            },
            *[{
                "message": content,
                "correct": False
            } for i, content in notes.items() if i != _id]
        ] if is_correct else [
            {
                "message": text,
                "correct": False
            }
        ]

    seen = sneknet.submit(options)

    log.debug(f'{seen=}')

    if seen:
        print(f'[{fore.CYAN}  SEEN  {style.RESET}]', end='')
    else:
        print(f'[{fore.MAGENTA} UNSEEN {style.RESET}]', end='')

    if (True in known.values() and not is_correct):
        print(f'[{back.RED}{fore.WHITE} WRONG {style.RESET}]', end='')
        log.warning(f'IMPOSTER MISMATCH: "{notes[_id]}" {text=} {_id=} {known=} {notes=}')

    print('')

    sys.stdout.write((
            '               '
            f'[ {style.DIM}{user["name"]}{style.RESET} ]'
            f'[ {style.UNDERLINED}TOTAL{style.RESET}: {styled_percent(total_games_won/total_games_played)} ]'
            f'[ {style.UNDERLINED}SESSION{style.RESET}: {styled_percent(session_games_won/session_games_played)} ]'
            f'[ {style.UNDERLINED}STREAK{style.RESET}: {win_streak} ]'
            f'[ {style.DIM}{session_games_played}{style.RESET} ]'
            '\r'
        ))
    sys.stdout.flush()
