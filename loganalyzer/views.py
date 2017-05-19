from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_required, login_user, logout_user, current_user

from loganalyzer import app, db, login_manager
from loganalyzer.forms import SBForm_base, SBForm_upload, LoginForm, SignupForm
from loganalyzer.models import User, SupportBundle, Tag


@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', new_sbs=SupportBundle.newest(5))


@app.route('/upload', methods=['GET','POST'])
@login_required
def upload():
    form = SBForm_upload()
    if form.validate_on_submit():
        service_request = form.service_request.data
        input_file = form.input_file.data
        comment = form.comment.data
        tags = form.tags.data
        sb = SupportBundle(service_request=service_request,filename=input_file.filename,comment=comment,
                           path='/tmp/{}'.format(input_file.filename), user=current_user, tags=tags)
        db.session.add(sb)
        db.session.commit()
        flash("Stored SR '{}', comment: '{}', filename: {}".format(service_request, comment, input_file.filename))
        return redirect(url_for('index'))
    return render_template('sb_form.html', form=form)


@app.route('/edit/<int:sb_id>', methods=['GET','POST'])
@login_required
def edit(sb_id):
    sb = SupportBundle.query.get_or_404(sb_id)
    if current_user != sb.user:
        abort(403)
    form = SBForm_base(obj=sb)
    if form.validate_on_submit():
        print(form.tags.data)
        form.populate_obj(sb)
        db.session.commit()
        flash("Stored '{}'".format(sb.id))
        return redirect(url_for('user', username=current_user.username))
    return render_template('sb_form.html', form=form, title="Edit Support Bundle")

@app.route('/delete/<int:sb_id>', methods=['POST','GET'])
@login_required
def delete_sb(sb_id):
    sb = SupportBundle.query.get_or_404(sb_id)
    if current_user != sb.user:
        abort(403)
    if request.method == "POST":
        db.session.delete(sb)
        db.session.commit()
        flash ("Deleted '{}'".format(sb.service_request))
        return redirect(url_for('user', username=current_user.username))
    else:
        flash("Please confirm deleting of this Support Bundle")
    return render_template('confirm_delete.html', supportbundle=sb, nolinks=True)

@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    #print(user.supportbundle)
    return render_template('user.html', user=user)

@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash("Logged in as {}".format(user.username))
            return redirect(request.args.get('next') or url_for('index'))
        flash("Incorrect username or password.")
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for('index'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,password=form.password.data, name=form.username.data, surname=form.username.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome, {}! Please log in'.format(user.username))
        return redirect(url_for('login'))
    return render_template("signup.html", form=form)

@app.route('/tag/<name>')
def tag(name):
    tag = Tag.query.filter_by(name=name).first_or_404()
    return render_template('tag.html', tag=tag)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

@app.context_processor
def inject_tags():
    return dict (all_tags=Tag.all)