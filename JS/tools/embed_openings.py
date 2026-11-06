"""Copies Openings.md into openings.html (inside the script tag with id openingsmd), so the page also works when opened from a file or without Openings.md next to it.
Run from the JS folder after editing Openings.md:  python tools/embed_openings.py"""
import re
CLOSE = '</' + 'script'
md = open('Openings.md', encoding='utf-8').read().replace('\r\n', '\n').replace(CLOSE, '<' + chr(92) + '/script')
p = 'openings.html'
s = open(p, encoding='utf-8').read()
s = re.sub(r'(<script id="openingsmd" type="text/plain">).*?(' + CLOSE + '>)', lambda m: m.group(1) + '\n' + md + m.group(2), s, flags=re.S)
open(p, 'w', encoding='utf-8').write(s)
print('embedded', len(md), 'characters')
