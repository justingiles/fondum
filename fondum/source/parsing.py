import creole as cr


# <<Anchor(anchorname)>>
def anchor_macro(text):
    t = text.strip()
    return unicode('<a id="{}"></a>'.format(t))


macros = {
    "Anchor": anchor_macro
}


def generate_html(article, page=None):
    src = ""
    default_text = getattr(page, "default_text", None)
    article_text = getattr(article, "s_creole_text", None)
    only_use_default_text = getattr(page, "only_use_default_text", False)
    if article_text and not only_use_default_text:
        src += cr.creole2html(article_text, macros=macros)
        src += "\n<br/>\n"
    elif default_text:
        src += cr.creole2html(unicode(default_text), macros=macros)
        src += "\n<br/>\n"
    if not src:
        if article is None:
            return "<i>Page Not Found</i>"
        return "<!-- empty article document -->"
    return src


def first_paragraph_html(orig_text):
    lines = orig_text.split("\n")
    for line in lines:
        t = line.strip()
        if t:
            html = cr.creole2html(unicode(t), macros=macros)
            # now, remove wrapping <p> tags
            html = html.replace('<p>', '')
            html = html.replace('</p>', '')
            return html
    return ""

# eof
