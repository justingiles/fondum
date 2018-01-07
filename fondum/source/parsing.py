import creole as cr
from jinja2 import Template
from app import g


# <<Anchor(anchorname)>>
def anchor_macro(text):
    t = text.strip()
    return unicode('<a id="{}"></a>'.format(t))


macros = {
    "Anchor": anchor_macro
}


def creole2html(creole_text):
    html = cr.creole2html(creole_text, macros=macros)
    return html


def generate_html(article, page=None):
    default_text = getattr(page, "default_text", None)
    article_text = getattr(article, "s_creole_text", None)
    only_use_default_text = getattr(page, "only_use_default_text", False)
    use_jinja = getattr(page, "use_jinja", True)
    default_text_data = getattr(page, "default_text_data", {})
    if article_text and not only_use_default_text:
        if use_jinja:
            template = Template(article_text)
            article_text = template.render(default_text_data)
        src = creole2html(article_text)
        src += "\n<br/>\n"
    elif default_text:
        if use_jinja:
            template = Template(default_text)
            default_text = template.render(default_text_data)
        src = cr.creole2html(unicode(default_text), macros=macros)
        src += "\n<br/>\n"
    else:
        src = ""
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
