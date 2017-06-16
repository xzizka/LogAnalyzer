from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user

from . import supportbundles
from .forms import SBForm_base, SBForm_upload, SBSearch
from .. import db
from ..models import User, SupportBundle, Tag
from ..analyzer.views import oracleSB

from pprint import pprint

@supportbundles.route('/upload', methods=['GET','POST'])
@login_required
def upload():
    form = SBForm_upload()
    if form.validate_on_submit():
        files = {}
        service_request = form.service_request.data
        input_file = form.input_file.data
        comment = form.comment.data
        tags = form.tags.data
        files = oracleSB(form.input_file.data)
        '''pprint(input_file.__dict__)
        
        sb = SupportBundle(service_request=service_request,filename=input_file.filename,comment=comment,
                           path='/tmp/{}'.format(input_file.filename), user=current_user, tags=tags)
        db.session.add(sb)
        db.session.commit()
        flash("Stored SR '{}', comment: '{}', filename: {}".format(service_request, comment, input_file.filename))
        '''
        #return redirect(url_for('main.index'))

        return render_template('files_display.html', files=files, sr=service_request)
    return render_template('sb_form.html', form=form)


@supportbundles.route('/edit/<int:sb_id>', methods=['GET','POST'])
@login_required
def edit(sb_id):
    sb = SupportBundle.query.get_or_404(sb_id)
    if current_user != sb.user:
        abort(403)
    form = SBForm_base(obj=sb)
    if form.validate_on_submit():
        form.populate_obj(sb)
        db.session.commit()
        flash("Stored '{}'".format(sb.id))
        return redirect(url_for('.user', username=current_user.username))
    return render_template('sb_form.html', form=form, title="Edit Support Bundle")


@supportbundles.route('/delete/<int:sb_id>', methods=['POST','GET'])
@login_required
def delete_sb(sb_id):
    sb = SupportBundle.query.get_or_404(sb_id)
    if current_user != sb.user:
        abort(403)
    if request.method == "POST":
        db.session.delete(sb)
        db.session.commit()
        flash ("Deleted '{}'".format(sb.service_request))
        return redirect(url_for('.user', username=current_user.username))
    else:
        flash("Please confirm deleting of this Support Bundle")
    return render_template('confirm_delete.html', supportbundle=sb, nolinks=True)


@supportbundles.route('/search/<int:sb_id>')
@supportbundles.route('/search/', defaults={ 'sb_id': None }, methods=['POST','GET'])
def search(sb_id):
    form = SBSearch()
    if form.validate_on_submit() or request.method == "GET":
        form.service_request.data = sb_id
    sbs = SupportBundle.query.filter_by(service_request = form.service_request.data)
    return render_template('sb_search.html', form=form, sbs=sbs)


@supportbundles.route('/display/<int:sb_id>', methods=['GET','POST'])
@login_required
def display(sb_id):
    return render_template('sb_display.html')


@supportbundles.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@supportbundles.route('/tag/<name>')
def tag(name):
    tag = Tag.query.filter_by(name=name).first_or_404()
    return render_template('tag.html', tag=tag)
