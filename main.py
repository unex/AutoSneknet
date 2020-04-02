import os
import sys
import re
import time
import random

from colored import fore, back, style

from api import GremlinsAPI, Sneknet

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

sneknet = Sneknet(SNEKNET_TOKEN)
gremlins = GremlinsAPI(REDDIT_TOKEN)

print(fore.GREEN_YELLOW)
print('🐍  https://snakeroom.org/sneknet 🐍')
print(style.RESET)

while True:
    room = gremlins.room()

    csrf = re_csrf.findall(room.text)[0]
    ids = re_notes_ids.findall(room.text)
    notes_content = re_notes.findall(room.text)

    notes = {ids[i]: notes_content[i] for i in range(len(ids))}

    # Query Sneknet for known, and remove known humans from the notes
    known = sneknet.query(notes_content)
    if True in known.values():
        print(f'[{fore.CYAN} IMPOSTER  {style.RESET}]', end='')
        # Sneknet doesnt return a full dict and it FUCKS my shit
        vals = [known.get(k, False) for k in range(5)]
        _id = ids[vals.index(True)]

        else:
        for i, v in known.items():
            del notes[ids[i]]

        if len(notes) == 1:
        print(f'[{fore.CYAN} IMPOSTER  {style.RESET}]', end='')
            _id = list(notes.keys())[0]

    else:
        print(f'[{fore.YELLOW} RANDOM {style.RESET}][{len(notes)}]', end='')
            _id = random.choice(list(notes.keys()))

    is_correct = gremlins.submit_guess(_id, csrf)

    text = notes[_id]

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

    print(f'[ {text:110} ]', end='')

    if is_correct:
        print(f'[{fore.LIGHT_GREEN} W {style.RESET}]', end='')
    else:
        print(f'[{fore.RED} L {style.RESET}]', end='')

    seen = sneknet.submit(options)

    if seen:
        print(f'[{fore.CYAN}  SEEN  {style.RESET}]', end='')
    else:
        print(f'[{fore.MAGENTA} UNSEEN {style.RESET}]', end='')

    if (True in known.values() and not is_correct):
        print(back.RED + fore.BLACK)
        print(f'\n\nOOH SHIT THIS SHOULD NEVER HAPPEN\n\n')
        print(f'{notes=}')
        print('\n')
        print(f'{notes[_id]} WAS WRONG!!!!')
        print(style.RESET + '\n\n')

    print('')

    time.sleep(.3)
