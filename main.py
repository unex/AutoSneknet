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

    imposter = None

    # Query Sneknet for known, and remove know humans from the notes
    known = sneknet.query(notes_content)
    for i, corr in known.items():
        if corr:
            imposter = i
            break

        else:
            to_del = []
            for _id, cont in notes.items():
                if cont == notes_content[i]:
                    to_del.append(_id)

            for _id in to_del:
                del notes[_id]
                ids.remove(_id)


    if imposter or len(notes) == 1:
        print(f'[{fore.CYAN} IMPOSTER  {style.RESET}]', end='')
        _id = ids[imposter] if imposter else ids[0]

    else:
        print(f'[{fore.YELLOW} RANDOM {style.RESET}][{len(notes)}]', end='')
        _id = random.choice(ids)

    if not notes:
        # This is very odd, not sure how to handle this
        continue

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

    print(f'[ {text:100} ]', end='')

    if is_correct:
        print(f'[{fore.LIGHT_GREEN} W {style.RESET}]', end='')
    else:
        print(f'[{fore.RED} L {style.RESET}]', end='')

    seen = sneknet.submit(options)

    if seen:
        print(f'[{fore.CYAN}  SEEN  {style.RESET}]', end='')
    else:
        print(f'[{fore.MAGENTA} UNSEEN {style.RESET}]', end='')

    if (imposter and not is_correct) or len(notes) == 0:
        print(back.RED + fore.BLACK)
        print(f'\n\nOOH SHIT THIS SHOULD NEVER HAPPEN\n\n')
        print(f'{notes=}, {imposter=}')
        print('\n')
        print(f'{notes[_id]} WAS WRONG!!!!')
        print(style.RESET + '\n\n')

    print('')

    time.sleep(.3)
