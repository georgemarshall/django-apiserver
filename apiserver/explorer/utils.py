from django.utils import simplejson

# encoding: utf-8

def linkify(thing):
    return '&quot;<a href="?endpoint={link}">{link}</a>&quot;'.format(link=thing.group(1))


def prettify(json):
    json = simplejson.loads(json)
    json = simplejson.dumps(json, sort_keys=True, indent=4)
    lexer = lexers.get_lexer_by_name("javascript")
    formatter = formatters.HtmlFormatter()
    html = highlight(json, lexer, formatter)
    return re.sub('&quot;(/.+)&quot;', linkify, html)