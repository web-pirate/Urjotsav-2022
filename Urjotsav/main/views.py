from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from Urjotsav.main.forms import RequestResetForm, ResetPasswordForm
from Urjotsav.models import User
from flask_login import current_user, logout_user, login_user, login_required
from Urjotsav import db
from datetime import timedelta
from itsdangerous import URLSafeTimedSerializer as URLSerializer
from itsdangerous import SignatureExpired, BadTimeSignature
from Urjotsav.main.utils import send_confirm_email, send_reset_email

main = Blueprint('main', __name__)

@main.route('/')
def home():
  """Home Route"""
  return render_template('index.html')

@main.route('/about/')
def about():
  """About Route"""
  return render_template('about.html')


@main.route('/register/', methods=['GET', 'POST'])
def register():
    """Registration Route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))
    if request.method == 'POST':
        if request.form.get('password') == request.form.get('cpassword'):
            if not User.query.filter_by(email=request.form.get('email')).first():
                s = URLSerializer(current_app.config['SECRET_KEY'])
                token = s.dumps({"name": request.form.get('name'), "email": request.form.get('email'), "Mobile Number": request.form.get('mobile_number'), "enrollment_number": request.form.get('enrollment_number'), 
                "branch": request.form.get('branch'), "dept_name": request.form.get('dept_name'), "password": request.form.get('password')},
                                salt="send-email-confirmation")
                send_confirm_email(email=request.form.get('email'), token=token)
                print('\n\n', request.form.get('branch'), request.form.get('dept_name'))

                flash(
                    f"An confirmation email has been sent to you on {request.form.get('email')}!", "success")
                return redirect(url_for('main.login'))
            else:
                flash(
                    f"You already have an account!", "info")
                return redirect(url_for('main.login'))
        else:
            flash(
                f"Please, check your password", "alert")
            return redirect(url_for('main.register'))
    return render_template('registration.html')


# ------ Confirm Registration ------ #
@main.route('/confirm_email/<token>/')
def confirm_email(token):
    s = URLSerializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token, salt="send-email-confirmation", max_age=600)
        is_piemr = False
        if data['email'].lower().strip().split('@')[-1] == 'piemr.edu.in':
            is_piemr = True
        user = User(name=data['name'], enrollment_number=data["enrollment_number"], email=data["email"], mobile_number=data['Mobile Number'], password=data["password"], 
                    dept_name=data['dept_name'], branch=data['branch'], role='Student', reward_points=0, is_piemr=is_piemr)
        db.session.add(user)
        db.session.commit()
        login_user(user)

        flash("Your account has been created successfully!", "alert")
        return redirect(url_for('main.profile'))
    except (SignatureExpired, BadTimeSignature):
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for('main.register'))


# ------ Reset Password Request Route ------ #
@main.route('/reset_password/', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password.", "info")
        return redirect(url_for('main.login'))
    return render_template('reset_request.html', form=form)


# ------ Reset Password <TOKEN> Route ------ #
@main.route('/reset_password/<token>/', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for('main.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        flash("Your password has been updated! You are now able to login", "success")
        return redirect(url_for('main.login'))
    return render_template('reset_token.html', form=form)


@main.route('/login/', methods=['GET', 'POST'])
def login():
    """Login Route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        print('\n\n',user.password)
        print('\n\n',request.form.get('password'))
        if user:
            if user.password == request.form.get('password'):
                login_user(user, remember=request.form.get('remember'),
                            duration=timedelta(weeks=3))
                next_page = request.args.get('next')

                flash("User logged in successfully!", "success")
                return redirect(next_page) if next_page else redirect(url_for('main.profile'))
            else:
                flash("Please check you password. Password don't match!", "danger")
                return redirect(url_for('main.login'))
        else:
            flash(
                "You don't have an account. Please create now to login.", "info")
            return redirect(url_for('main.register'))
    return render_template('login.html')


@main.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    """Profile Route"""
    return render_template('profile.html')


@main.route('/gallery/')
def gallery():
    """Gallery Route"""
    return render_template('gallery.html')

@main.route('/dashboard/')
@login_required
def dashboard():
    return "Dashboard"


@main.route('/logout/')
@login_required
def logout():
    """Logout Route"""
    logout_user()
    flash("Logout successfully!", "success")
    return redirect(url_for('main.login'))
