# import os
import re

raw_title_flags = [
    ' ',
]

replace_by_default = [
    ('_', ' '),
]

replace_final = [
    ('-', ' '),
]


leading_year = re.compile(r'^(\d{4})\W')
language_info = re.compile(r'\W+(cn|en)\b')
edition_info = re.compile(r'\W+(1st|2nd|3rd|\dth|ed\d)\b.*$')


def extract_info(raw_filename, **kwargs):
    info = {}

    title = raw_filename
    m = leading_year.findall(title)
    if m:
        info['year'] = int(m[0])
        title = title[5:]

    for c1, c2 in replace_by_default:
        title = title.replace(c1, c2)

    m = language_info.findall(title)
    if m:
        info['language'] = m[0]
        title = re.sub(language_info, '', title)

    m = edition_info.findall(title)
    if m:
        info['edition'] = m[0]
        title = re.sub(edition_info, '', title)

    should_replace_final = True
    for c in raw_title_flags:
        if c in title:
            should_replace_final = False
            break

    if should_replace_final:
        for c1, c2 in replace_final:
            title = title.replace(c1, c2)

    info['title'] = title.title()

    return info
