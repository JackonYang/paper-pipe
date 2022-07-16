import re

title_format_re = re.compile(r'[\W\s]+')


def gen_meta_key(title, year=None):
    t = title_format_re.sub('-', title.lower()).strip(' -')
    if year is not None:
        return '%s-%s' % (year, t)
    else:
        return t
