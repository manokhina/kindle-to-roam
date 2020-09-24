import re
from collections import defaultdict

CLIPPINGS_PATH = "/Volumes/Kindle/documents/My Clippings.txt"

with open(CLIPPINGS_PATH, 'r') as f:
    clippings = f.read()

notes = [s.strip('\n').strip('\ufeff') for s in clippings.split('==========')]

page = """
- Metadata
    - Author:: {author}
    - Tags:: 
    - Type:: 
    - Status:: 
    - Source:: 
- :hiccup [:hr]
{note}
"""

result = defaultdict(list)
for note in notes:
    header = note.split('\n')[0]
    title = header.split(" (")[0]
    r = re.search(r'(?<=\()[^.]*', header[:-1])
    author = r.group() if r else ''

    head = (title, author)

    if 'Ваш выделенный отрывок в месте' in note:
        text = note.split('\n\n')[-1]
        previous_chunk = result[head][-1].strip("\n") if result[head] else None
        if result[head] and previous_chunk and text.startswith(previous_chunk.strip("- ")):
            del result[head][-1]
        if result[head] and previous_chunk.endswith(text): continue
        result[head].append(f"- {text}\n")

for book, note in result.items():
    page_title = book[0]
    author = book[1]
    note = ''.join(note)
    content = page.format(author=author, note=note)
    with open(f"{page_title}.md", 'w') as f:
        f.write(content)
