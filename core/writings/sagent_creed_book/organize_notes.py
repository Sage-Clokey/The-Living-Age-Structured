import json
import os
import re

# Load notes
with open('/mnt/c/Users/SajcS/Desktop/sagent creed book/notes.json', encoding='utf-8') as f:
    notes = json.load(f)

BASE = '/mnt/c/Users/SajcS/Desktop/sagent creed book'

FOLDERS = {
    'Prologue':                                             'Prologue',
    'Part I - The Pledge of the Heart':                    'Part I - The Pledge of the Heart',
    'Part II - The Creed - Aphorisms of the Sagent':       'Part II - The Creed - Aphorisms of the Sagent',
    'Part III - The Divine Creed':                         'Part III - The Divine Creed',
    'Part IV - The True Republic':                         'Part IV - The True Republic',
    'Part V - The Galaxy, the Cave, and the Creed':        'Part V - The Galaxy, the Cave, and the Creed',
    'Part VI - Who I Am':                                  'Part VI - Who I Am',
    'Part VII - The Pattern':                              'Part VII - The Pattern',
    'Part VIII - The Shield':                              'Part VIII - The Shield',
    'Part IX - The Prestige':                              'Part IX - The Prestige',
    'Epilogue':                                            'Epilogue',
    'Miscellaneous':                                       'Miscellaneous',
}

# Map first-8-chars of note ID -> folder key
ASSIGNMENT = {
    # PROLOGUE
    'fb64c856': 'Prologue',
    '81fcce9f': 'Prologue',

    # PART I - Love / Romance
    '5bd35602': 'Part I - The Pledge of the Heart',
    '268cd399': 'Part I - The Pledge of the Heart',
    'e499da0f': 'Part I - The Pledge of the Heart',
    'adf2c352': 'Part I - The Pledge of the Heart',
    'ecb0d868': 'Part I - The Pledge of the Heart',
    '06b73d74': 'Part I - The Pledge of the Heart',
    'e45f860a': 'Part I - The Pledge of the Heart',
    'c7f42e0c': 'Part I - The Pledge of the Heart',
    '107ba385': 'Part I - The Pledge of the Heart',
    '5d4607e7': 'Part I - The Pledge of the Heart',
    '6918bf98': 'Part I - The Pledge of the Heart',
    '757c02aa': 'Part I - The Pledge of the Heart',
    'affaa30c': 'Part I - The Pledge of the Heart',
    '731a79ed': 'Part I - The Pledge of the Heart',
    '0f12581f': 'Part I - The Pledge of the Heart',
    '0f48eb8c': 'Part I - The Pledge of the Heart',
    '6eef2db7': 'Part I - The Pledge of the Heart',
    '44c8c616': 'Part I - The Pledge of the Heart',
    '0d2b29f8': 'Part I - The Pledge of the Heart',
    '064d2b47': 'Part I - The Pledge of the Heart',
    '25d94ce1': 'Part I - The Pledge of the Heart',
    '4872d5f5': 'Part I - The Pledge of the Heart',
    '25d3bf28': 'Part I - The Pledge of the Heart',
    '44d20d0e': 'Part I - The Pledge of the Heart',
    'b5d06c8f': 'Part I - The Pledge of the Heart',
    '5fff0381': 'Part I - The Pledge of the Heart',
    '4caf7bb5': 'Part I - The Pledge of the Heart',
    '07dd4659': 'Part I - The Pledge of the Heart',
    '2b316034': 'Part I - The Pledge of the Heart',
    '35ed2081': 'Part I - The Pledge of the Heart',
    '2da7502b': 'Part I - The Pledge of the Heart',
    'd1e3e905': 'Part I - The Pledge of the Heart',
    '96fd899d': 'Part I - The Pledge of the Heart',
    '83514c2d': 'Part I - The Pledge of the Heart',

    # PART II - Philosophy / Wisdom
    '882a4268': 'Part II - The Creed - Aphorisms of the Sagent',
    'eee73933': 'Part II - The Creed - Aphorisms of the Sagent',
    'e0238d69': 'Part II - The Creed - Aphorisms of the Sagent',
    'fbf3f074': 'Part II - The Creed - Aphorisms of the Sagent',
    'e639d284': 'Part II - The Creed - Aphorisms of the Sagent',
    '920dd968': 'Part II - The Creed - Aphorisms of the Sagent',
    '296440f6': 'Part II - The Creed - Aphorisms of the Sagent',
    'aa5c0538': 'Part II - The Creed - Aphorisms of the Sagent',
    '1055b9b9': 'Part II - The Creed - Aphorisms of the Sagent',
    'c347cd8d': 'Part II - The Creed - Aphorisms of the Sagent',
    '02b756ec': 'Part II - The Creed - Aphorisms of the Sagent',
    'dfd935f6': 'Part II - The Creed - Aphorisms of the Sagent',
    '9911e141': 'Part II - The Creed - Aphorisms of the Sagent',
    'd341005e': 'Part II - The Creed - Aphorisms of the Sagent',
    'd04e025c': 'Part II - The Creed - Aphorisms of the Sagent',
    '37c8100e': 'Part II - The Creed - Aphorisms of the Sagent',
    '7350d95c': 'Part II - The Creed - Aphorisms of the Sagent',
    '37b911b1': 'Part II - The Creed - Aphorisms of the Sagent',
    '78c395bc': 'Part II - The Creed - Aphorisms of the Sagent',
    '28f558e7': 'Part II - The Creed - Aphorisms of the Sagent',
    'd09ba956': 'Part II - The Creed - Aphorisms of the Sagent',
    '37e578bc': 'Part II - The Creed - Aphorisms of the Sagent',
    '9da10ac9': 'Part II - The Creed - Aphorisms of the Sagent',
    'c176e887': 'Part II - The Creed - Aphorisms of the Sagent',
    '561f0858': 'Part II - The Creed - Aphorisms of the Sagent',
    '5efe51f6': 'Part II - The Creed - Aphorisms of the Sagent',
    '2d8df620': 'Part II - The Creed - Aphorisms of the Sagent',
    '197e2910': 'Part II - The Creed - Aphorisms of the Sagent',
    '3c7a48db': 'Part II - The Creed - Aphorisms of the Sagent',
    '1a3e042e': 'Part II - The Creed - Aphorisms of the Sagent',
    '392dc4a5': 'Part II - The Creed - Aphorisms of the Sagent',
    '60815bbf': 'Part II - The Creed - Aphorisms of the Sagent',
    'bea76673': 'Part II - The Creed - Aphorisms of the Sagent',
    '6f95609f': 'Part II - The Creed - Aphorisms of the Sagent',
    'd2152055': 'Part II - The Creed - Aphorisms of the Sagent',
    '8711040e': 'Part II - The Creed - Aphorisms of the Sagent',
    '33da7e99': 'Part II - The Creed - Aphorisms of the Sagent',
    'a9008172': 'Part II - The Creed - Aphorisms of the Sagent',
    '11d7829d': 'Part II - The Creed - Aphorisms of the Sagent',
    '4c8b304c': 'Part II - The Creed - Aphorisms of the Sagent',
    'b491d23f': 'Part II - The Creed - Aphorisms of the Sagent',
    'd167e496': 'Part II - The Creed - Aphorisms of the Sagent',
    'a9bed7db': 'Part II - The Creed - Aphorisms of the Sagent',
    'cd30d18f': 'Part II - The Creed - Aphorisms of the Sagent',
    'c2b40ff3': 'Part II - The Creed - Aphorisms of the Sagent',
    '1fcca7ab': 'Part II - The Creed - Aphorisms of the Sagent',
    '6af82f53': 'Part II - The Creed - Aphorisms of the Sagent',
    '4a96f87b': 'Part II - The Creed - Aphorisms of the Sagent',
    '642cb4d2': 'Part II - The Creed - Aphorisms of the Sagent',
    '94998cfe': 'Part II - The Creed - Aphorisms of the Sagent',
    '6767fd1c': 'Part II - The Creed - Aphorisms of the Sagent',
    'd64c031a': 'Part II - The Creed - Aphorisms of the Sagent',
    '365ae169': 'Part II - The Creed - Aphorisms of the Sagent',

    # PART III - Spirituality / Faith
    '2f4dfc79': 'Part III - The Divine Creed',
    '620387d3': 'Part III - The Divine Creed',
    '47c4c7b5': 'Part III - The Divine Creed',
    '726579b2': 'Part III - The Divine Creed',
    '27994f84': 'Part III - The Divine Creed',
    'c7f4fcf0': 'Part III - The Divine Creed',
    '5598c222': 'Part III - The Divine Creed',
    '0ba7411a': 'Part III - The Divine Creed',
    'e3ebd82f': 'Part III - The Divine Creed',
    '5a7dae0c': 'Part III - The Divine Creed',
    '72232e6e': 'Part III - The Divine Creed',
    'add896e3': 'Part III - The Divine Creed',
    '8e2dfd28': 'Part III - The Divine Creed',
    'e0699be0': 'Part III - The Divine Creed',
    'acef3618': 'Part III - The Divine Creed',
    '5404338c': 'Part III - The Divine Creed',
    '645e3bd7': 'Part III - The Divine Creed',
    '994a01c0': 'Part III - The Divine Creed',
    'f907a38c': 'Part III - The Divine Creed',
    'bc2eb4c9': 'Part III - The Divine Creed',
    '5c5576fd': 'Part III - The Divine Creed',
    '16cde256': 'Part III - The Divine Creed',
    '951ede58': 'Part III - The Divine Creed',
    '79106a5a': 'Part III - The Divine Creed',
    'e1ceda42': 'Part III - The Divine Creed',
    '0c51cea6': 'Part III - The Divine Creed',
    '2768b835': 'Part III - The Divine Creed',
    'f620da7c': 'Part III - The Divine Creed',
    '96c636a9': 'Part III - The Divine Creed',
    '9d9bd1c0': 'Part III - The Divine Creed',
    '0cc367e4': 'Part III - The Divine Creed',
    '6b99ee93': 'Part III - The Divine Creed',
    '9b5b406c': 'Part III - The Divine Creed',
    '564a4a95': 'Part III - The Divine Creed',
    'b1833b1e': 'Part III - The Divine Creed',

    # PART IV - Political / Societal
    'f00ce29e': 'Part IV - The True Republic',
    '57b6e06f': 'Part IV - The True Republic',
    'c2753943': 'Part IV - The True Republic',
    '309aff1c': 'Part IV - The True Republic',
    '22d11eb4': 'Part IV - The True Republic',
    '84ec62d6': 'Part IV - The True Republic',
    '0d758c89': 'Part IV - The True Republic',
    '3c4217b7': 'Part IV - The True Republic',
    '372a8ad0': 'Part IV - The True Republic',
    '7d4993dc': 'Part IV - The True Republic',
    'c45acaf7': 'Part IV - The True Republic',
    'a396f87b': 'Part IV - The True Republic',
    '23536538': 'Part IV - The True Republic',
    '82c3dd0a': 'Part IV - The True Republic',
    '0579aa37': 'Part IV - The True Republic',
    'f9a9c11c': 'Part IV - The True Republic',
    '7bf93a69': 'Part IV - The True Republic',
    '265a67d7': 'Part IV - The True Republic',
    '7658e757': 'Part IV - The True Republic',
    '3775e3c7': 'Part IV - The True Republic',
    'cadf120c': 'Part IV - The True Republic',
    'ba12decc': 'Part IV - The True Republic',
    '0b768cb5': 'Part IV - The True Republic',
    '51f85ad8': 'Part IV - The True Republic',
    '939e749b': 'Part IV - The True Republic',
    'cde14216': 'Part IV - The True Republic',
    'eeb3a75b': 'Part IV - The True Republic',
    '01d234a7': 'Part IV - The True Republic',
    'e99651f0': 'Part IV - The True Republic',
    'a970ad1f': 'Part IV - The True Republic',
    'fe798283': 'Part IV - The True Republic',
    '77e218fb': 'Part IV - The True Republic',
    '1a88cff7': 'Part IV - The True Republic',
    '38584e07': 'Part IV - The True Republic',
    'f894273f': 'Part IV - The True Republic',
    '6aec5b5e': 'Part IV - The True Republic',
    '8275a5fb': 'Part IV - The True Republic',
    '928693f6': 'Part IV - The True Republic',
    'fa9d079a': 'Part IV - The True Republic',
    '70d66cc5': 'Part IV - The True Republic',
    '0c25c0da': 'Part IV - The True Republic',
    '9396840a': 'Part IV - The True Republic',
    '196c636a': 'Part IV - The True Republic',
    '7b673045': 'Part IV - The True Republic',
    'b148f7fc': 'Part IV - The True Republic',

    # PART V - Pop Culture
    'a56ef28a': 'Part V - The Galaxy, the Cave, and the Creed',
    '5c461e4a': 'Part V - The Galaxy, the Cave, and the Creed',
    '989c4bc7': 'Part V - The Galaxy, the Cave, and the Creed',
    '989c4bc8': 'Part V - The Galaxy, the Cave, and the Creed',
    '989c4b98': 'Part V - The Galaxy, the Cave, and the Creed',
    '180f6687': 'Part V - The Galaxy, the Cave, and the Creed',
    '2d3bd6cb': 'Part V - The Galaxy, the Cave, and the Creed',
    'f25da01c': 'Part V - The Galaxy, the Cave, and the Creed',
    '39e7c974': 'Part V - The Galaxy, the Cave, and the Creed',
    '6e566c99': 'Part V - The Galaxy, the Cave, and the Creed',
    '00968baa': 'Part V - The Galaxy, the Cave, and the Creed',
    'f0f47fb9': 'Part V - The Galaxy, the Cave, and the Creed',
    '755dd903': 'Part V - The Galaxy, the Cave, and the Creed',
    '71218627': 'Part V - The Galaxy, the Cave, and the Creed',
    'bf842e86': 'Part V - The Galaxy, the Cave, and the Creed',
    'b5e1b540': 'Part V - The Galaxy, the Cave, and the Creed',
    '754421bf': 'Part V - The Galaxy, the Cave, and the Creed',
    '42b3ebaa': 'Part V - The Galaxy, the Cave, and the Creed',
    '3121f219': 'Part V - The Galaxy, the Cave, and the Creed',
    'dbbf006e': 'Part V - The Galaxy, the Cave, and the Creed',
    '95548639': 'Part V - The Galaxy, the Cave, and the Creed',
    'b2754c24': 'Part V - The Galaxy, the Cave, and the Creed',
    '7920eef5': 'Part V - The Galaxy, the Cave, and the Creed',
    'a4df66dc': 'Part V - The Galaxy, the Cave, and the Creed',
    'dfb13902': 'Part V - The Galaxy, the Cave, and the Creed',
    '434a95db': 'Part V - The Galaxy, the Cave, and the Creed',
    'd3fbf4e2': 'Part V - The Galaxy, the Cave, and the Creed',
    '83a514c2': 'Part V - The Galaxy, the Cave, and the Creed',
    '9e1d688c': 'Part V - The Galaxy, the Cave, and the Creed',
    '7cd6d458': 'Part V - The Galaxy, the Cave, and the Creed',
    '0e9fc881': 'Part V - The Galaxy, the Cave, and the Creed',
    '81612fa0': 'Part V - The Galaxy, the Cave, and the Creed',
    '984d465c': 'Part V - The Galaxy, the Cave, and the Creed',
    'ea1d24c0': 'Part V - The Galaxy, the Cave, and the Creed',
    '488538ba': 'Part V - The Galaxy, the Cave, and the Creed',
    'ec68adae': 'Part V - The Galaxy, the Cave, and the Creed',
    '89f258eb': 'Part V - The Galaxy, the Cave, and the Creed',
    'b928bbad': 'Part V - The Galaxy, the Cave, and the Creed',
    '1b7e10c4': 'Part V - The Galaxy, the Cave, and the Creed',
    '98db5353': 'Part V - The Galaxy, the Cave, and the Creed',
    '940f2b47': 'Part V - The Galaxy, the Cave, and the Creed',
    '097f5116': 'Part V - The Galaxy, the Cave, and the Creed',
    'a10a6e30': 'Part V - The Galaxy, the Cave, and the Creed',
    'ecc69b36': 'Part V - The Galaxy, the Cave, and the Creed',
    '906353d1': 'Part V - The Galaxy, the Cave, and the Creed',
    '91367ea5': 'Part V - The Galaxy, the Cave, and the Creed',
    'e4aea2d0': 'Part V - The Galaxy, the Cave, and the Creed',
    'd13c5b11': 'Part V - The Galaxy, the Cave, and the Creed',
    'f5815b92': 'Part V - The Galaxy, the Cave, and the Creed',
    'e3840d68': 'Part V - The Galaxy, the Cave, and the Creed',
    '234eed39': 'Part V - The Galaxy, the Cave, and the Creed',
    '6659f379': 'Part V - The Galaxy, the Cave, and the Creed',
    'b8b6da87': 'Part V - The Galaxy, the Cave, and the Creed',
    'd12d3318': 'Part V - The Galaxy, the Cave, and the Creed',
    '386da1e1': 'Part V - The Galaxy, the Cave, and the Creed',
    '6d2b3e97': 'Part V - The Galaxy, the Cave, and the Creed',

    # PART VI - Identity / The Sagent
    '2d874ee4': 'Part VI - Who I Am',
    'b307b488': 'Part VI - Who I Am',
    '54787c2a': 'Part VI - Who I Am',
    'e982e5b0': 'Part VI - Who I Am',
    '2e6e9e83': 'Part VI - Who I Am',
    'faa3b0e0': 'Part VI - Who I Am',
    'f0875f5b': 'Part VI - Who I Am',
    'd299ee18': 'Part VI - Who I Am',
    'deadaf71': 'Part VI - Who I Am',
    '2332e558': 'Part VI - Who I Am',
    '61d28bcf': 'Part VI - Who I Am',
    '61a3d54a': 'Part VI - Who I Am',
    '7b80a344': 'Part VI - Who I Am',
    '38317a3a': 'Part VI - Who I Am',
    '7372dd53': 'Part VI - Who I Am',
    'f8a9eec9': 'Part VI - Who I Am',
    'dc1561fa': 'Part VI - Who I Am',
    '2e5329f6': 'Part VI - Who I Am',
    '140a1827': 'Part VI - Who I Am',
    '66123e51': 'Part VI - Who I Am',
    '4cdde5df': 'Part VI - Who I Am',
    'f5c6e38c': 'Part VI - Who I Am',
    '82688fe3': 'Part VI - Who I Am',
    '8c915868': 'Part VI - Who I Am',
    '096b554c': 'Part VI - Who I Am',
    '508c5a89': 'Part VI - Who I Am',
    'e6fbc6b2': 'Part VI - Who I Am',
    'f71c8041': 'Part VI - Who I Am',
    '12665384': 'Part VI - Who I Am',
    '1be18e62': 'Part VI - Who I Am',
    '8be633bb': 'Part VI - Who I Am',
    '6b8df81a': 'Part VI - Who I Am',
    'c8873fbd': 'Part VI - Who I Am',
    '6e9b7bbf': 'Part VI - Who I Am',
    '691db036': 'Part VI - Who I Am',

    # PART VII - Numerology / Spirals / Hypertime
    'cf7fa869': 'Part VII - The Pattern',
    '07b0ac65': 'Part VII - The Pattern',
    '6f19700b': 'Part VII - The Pattern',
    'ca8cc0c2': 'Part VII - The Pattern',
    'e3b11555': 'Part VII - The Pattern',
    'f3f4d8b4': 'Part VII - The Pattern',
    '7f9e9f53': 'Part VII - The Pattern',
    '995d3138': 'Part VII - The Pattern',
    '68ace97f': 'Part VII - The Pattern',
    'a9eea2c9': 'Part VII - The Pattern',
    '353a7bbd': 'Part VII - The Pattern',
    '98060e19': 'Part VII - The Pattern',

    # PART VIII - Guardian / Protection
    'b719bc18': 'Part VIII - The Shield',
    'd185e293': 'Part VIII - The Shield',
    'a510fb87': 'Part VIII - The Shield',
    '409c9a33': 'Part VIII - The Shield',
    'ae080f58': 'Part VIII - The Shield',
    '31d48fe9': 'Part VIII - The Shield',
    '868b8bed': 'Part VIII - The Shield',
    '51c8b65a': 'Part VIII - The Shield',
    '265a67d8': 'Part VIII - The Shield',  # note: 265a67d7 above is in Part IV
    '2649be75': 'Part VIII - The Shield',
    '8305c33a': 'Part VIII - The Shield',
    '178f6687': 'Part VIII - The Shield',

    # PART IX - Narrative / Prestige / Storytelling
    '4da4ff04': 'Part IX - The Prestige',
    'b6cde4b9': 'Part IX - The Prestige',
    'd708b293': 'Part IX - The Prestige',
    '54916e4a': 'Part IX - The Prestige',
    '48879b95': 'Part IX - The Prestige',
    '9671a186': 'Part IX - The Prestige',
    'd5659e70': 'Part IX - The Prestige',
    '2f6fd2ef': 'Part IX - The Prestige',
    '0fa228ad': 'Part IX - The Prestige',
    'e8bef125': 'Part IX - The Prestige',
    '317b2a4b': 'Part IX - The Prestige',
    'f311283d': 'Part IX - The Prestige',
    '15db23ee': 'Part IX - The Prestige',
    '626a1357': 'Part IX - The Prestige',
    'a7772fa8': 'Part IX - The Prestige',
    'db1eed39': 'Part IX - The Prestige',
    'f8a6e53c': 'Part IX - The Prestige',
    '0ce9a836': 'Part IX - The Prestige',
    '192b8c92': 'Part IX - The Prestige',

    # EPILOGUE
    # ec68adae is already in Part V; put these extras in Epilogue
    'c9b7cc9f': 'Epilogue',

    # MISC
    'c65b3c65': 'Miscellaneous',
    '5f4889ad': 'Miscellaneous',
    '96f34d7d': 'Miscellaneous',
    'a473412e': 'Miscellaneous',
}

def sanitize_filename(title, note_id):
    # Remove/replace filesystem-unsafe characters
    safe = re.sub(r'[\\/:*?"<>|]', '', title)
    safe = safe.strip()
    safe = safe[:80]  # max 80 chars for title portion
    if not safe or safe.lower() == 'untitled note':
        safe = 'Untitled Note'
    # Append short ID to ensure uniqueness
    short_id = note_id[:8]
    return f"{safe} [{short_id}].txt"

# Create all folders
for folder_name in FOLDERS.values():
    folder_path = os.path.join(BASE, folder_name)
    os.makedirs(folder_path, exist_ok=True)

placed = 0
unmatched = 0

for note in notes:
    note_id = note.get('id', '')
    prefix = note_id[:8]
    title = note.get('title', 'Untitled Note') or 'Untitled Note'
    content = note.get('content', '') or ''
    created = note.get('createdAt', '')
    updated = note.get('updatedAt', '')

    folder_key = ASSIGNMENT.get(prefix)
    if folder_key is None:
        folder_key = 'Miscellaneous'
        unmatched += 1

    folder_path = os.path.join(BASE, folder_key)
    filename = sanitize_filename(title, note_id)
    filepath = os.path.join(folder_path, filename)

    file_content = f"Title: {title}\nCreated: {created}\nUpdated: {updated}\nID: {note_id}\n\n---\n\n{content}\n"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(file_content)

    placed += 1

print(f"Done. {placed} notes written. {unmatched} placed in Miscellaneous (no explicit mapping).")

# Print summary
for folder_name in FOLDERS.values():
    folder_path = os.path.join(BASE, folder_name)
    count = len([f for f in os.listdir(folder_path) if f.endswith('.txt')])
    print(f"  {folder_name}: {count} notes")
