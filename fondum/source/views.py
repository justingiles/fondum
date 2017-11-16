from app import app
from flask import Flask, request, g, redirect, url_for, \
    render_template, send_file, send_from_directory, abort
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
import os
from werkzeug.wrappers import Response

import msg
import admin__database as database
import parsing
from s3 import s3_upload, static_proxy


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static/img'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


@app.route('/apic/<pic_key>.png')
def display_article_picture(pic_key):
    pic = database.read_articlePicture(pic_key)
    if pic:
        return static_proxy(pic.s_etag)
    return abort(404)


@app.route('/<group_name>/<page_name>/')
def document_page(group_name, page_name):
    key = database.build_key(group_name, page_name)
    article = database.read_article_byKey(key)
    if article is None:
        return render_template(
            'reference-not-found.html',
            group_name=group_name,
            page_name=page_name
        )
    html = parsing.generate_html(article)
    return render_template(
        'document.html',
        article=article,
        html=html
    )


def page_handler(page, source_def, key, **kwargs):
    if msg.is_bad(page.status):
        msg.flash(page.status)
        return redirect(url_for('index'))
    if page.login_required:
        if not current_user.is_authenticated:
            msg.flash('You must be logged in.', t="warning")
            return redirect(url_for('index'))
    #
    # handle purposeful bypass
    #
    if hasattr(page, "fondum_bypass"):
        return page.fondum_bypass(**kwargs)
    #
    # form handling
    #
    if page.wtf:
        if page.wtf.validate_on_submit():
            if not hasattr(page.wtf, "process_form"):
                msg.flash('FONDUM error: no process_form method found', t="bug")
                return redirect(url_for(source_def))
            result = page.wtf.process_form(page.wtf, **kwargs)
            if isinstance(result, Response):
                return result
            msg.flash(result)
            if result.return_def:
                if result.return_def_parms:
                    return redirect(url_for(result.return_def, **result.return_def_parms))
                return redirect(url_for(result.return_def))
            return redirect(url_for(source_def, **kwargs))
        else:
            if hasattr(page.wtf, 'set_starting_values'):
                result = page.wtf.set_starting_values(**kwargs)
                if msg.is_msg(result):
                    msg.flash(result)
                    if result.return_def:
                        if result.return_def_parms:
                            return redirect(url_for(result.return_def, **result.return_def_parms))
                        return redirect(url_for(result.return_def))
    #
    # generate html
    #
    article = database.read_article_byKey(key)
    html = parsing.generate_html(article, page)
    #
    #
    return render_template(
        'page.html',
        page=page,
        key=key,
        html=html
    )

# {{{--INSERT-MARKER--}}}


# eof
