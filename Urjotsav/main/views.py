from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from Urjotsav.main.forms import RequestResetForm, ResetPasswordForm
from Urjotsav.models import User, EventRegistration, Events, Department, Payments
from flask_login import current_user, logout_user, login_user, login_required
from Urjotsav import db
from datetime import timedelta, datetime
import pytz
from itsdangerous import URLSafeTimedSerializer as URLSerializer
from itsdangerous import SignatureExpired, BadTimeSignature
import random
import string
from Urjotsav.main.utils import send_confirm_email, send_reset_email, send_event_registration_link, send_event_registration_link_co_ordinator

main = Blueprint('main', __name__)
tz = pytz.timezone('Asia/Calcutta')

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
            if not User.query.filter_by(email=request.form.get('email')).first() or not User.query.filter_by(email=request.form.get('mobile_number')).first():
                s = URLSerializer(current_app.config['SECRET_KEY'])
                token = s.dumps({"name": request.form.get('name'), "email": request.form.get('email'), "Mobile Number": request.form.get('mobile_number'), "enrollment_number": request.form.get('enrollment_number'), "dept_name": request.form.get('dept_name'), "password": request.form.get('password')},
                                salt="send-email-confirmation")
                send_confirm_email(email=request.form.get('email'), token=token)

                flash(
                    f"An confirmation email has been sent to you on {request.form.get('email')}!", "success")
                return redirect(url_for('main.login'))
            else:
                flash(
                    f"You already have an account! Either Email or EnrollmentNumber or Mobile Number is already in use.", "info")
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
                    dept_name=data['dept_name'], role='Student', reward_points=0, is_piemr=is_piemr)
        db.session.add(user)
        db.session.commit()
        login_user(user)

        flash("Your account has been created successfully!", "success")
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


@main.route('/logout/')
@login_required
def logout():
    """Logout Route"""
    logout_user()
    flash("Logout successfully!", "success")
    return redirect(url_for('main.login'))


@main.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    """Profile Route"""
    if current_user.role != "Student":
        return redirect(url_for('main.dashboard'))
    total_amount = 0
    events = EventRegistration.query.filter_by(user_id=current_user.id).all()
    for event in events:
        total_amount += int(event.fees)
    return render_template('profile.html', events=events, total_amount=total_amount)


@main.route('/event/<event_type>/')
def event(event_type):
    """All Event Route"""
    events = Events.query.filter_by(event_type=event_type).all()
    current_event = ''
    if event_type == "cultural":
        current_event = "Cultural"
    elif event_type == "managerial":
        current_event = "Managerial"
    elif event_type == "sports":
        current_event = "Sports"
    elif event_type == "technical":
        current_event = "Technical"
    return render_template('event.html', events=events, current_event=current_event)


@main.route('/event_registration/<event_name>/', methods=['GET', 'POST'])
@login_required
def event_registration(event_name):
    """Event Registration"""
    if request.method == 'POST':
        current_registrations = EventRegistration.query.filter_by(user_id=current_user.id).filter_by(event_name=event_name).all()
        is_already_registered = False
        if len(current_registrations) > 0:
            is_already_registered = True
        if not is_already_registered:
            team_size = request.form.get('groupNo')
            events = Events.query.filter_by(event_name=event_name).first()
            main_co_ordinator = events.main_co_ordinator
            user = User.query.filter_by(id=main_co_ordinator).first()
            event_type = events.event_type
            if current_user.is_piemr:
                fees = events.in_entry_fees
            else:
                fees = events.out_entry_fees
            date = events.event_date.date()
            venue = events.venue

            pay_id = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=25))
            pay = Payments(amount=fees, payment_id=pay_id, date=datetime.now(tz), status='Processing', user_id=current_user.id)
            eve = EventRegistration(event_type=event_type, event_name=event_name, fees=fees, date=date, venue=venue, 
            team_size=team_size, team_members=current_user.name, team_members_id=current_user.id, paid=0, team_leader=current_user.name, pay_id=pay_id, mobile_number=current_user.mobile_number, 
            user_id=current_user.id)
            db.session.add(eve)
            db.session.add(pay)
            dept = Department.query.filter_by(dept_name=current_user.dept_name).first()
            current_user.reward_points += events.reward_points
            dept.reward_points += events.reward_points
            db.session.commit()
            message = f"Registration for {event_name.title()} is successful. Approval request has been sent to respective Co-ordinator."
            if int(team_size) > 1:
                message = f"Registration for {event_name.title()} is successful. Approval request has been sent to respective Co-ordinator. Registration link has been generated and sent to your registered email id. kindly, read the instructions carefully."
                send_event_registration_link(email=current_user.email, event_name=event_name, team_leader=current_user.name, pay_id=pay_id)
            send_event_registration_link_co_ordinator(email=user.email, event_name=event_name, team_leader=current_user.name, pay_id=pay_id)
            flash(f"{message}", "success")
            return redirect(url_for('main.profile'))
        flash("You already registered for this event.", "info")
        return redirect(url_for('main.profile'))
    return render_template('event_register.html', event_name=event_name)


@main.route('/event_registration/<event_name>/<team_leader>/<pay_id>/')
@login_required
def event_registration_team_members(event_name, team_leader, pay_id):
    event = EventRegistration.query.filter_by(pay_id=pay_id).filter_by(team_leader=team_leader).filter_by(event_name=event_name).first()
    team_names = event.team_members.split(', ')
    team_names_id = event.team_members_id.split(', ')
    if len(team_names_id) < event.team_size:
        if str(current_user.id) in team_names_id:
            flash(f"You already registered for {event_name}.", "info")
            return redirect(url_for('main.profile'))
        else:
            team_names.append(current_user.name)
            team_names_id.append(str(current_user.id))
            event.team_members = ', '.join(team_names)
            event.team_members_id = ', '.join(team_names_id)
            eve = Events.query.filter_by(event_name=event_name).first()
            current_user.reward_points += eve.reward_points
            dept = Department.query.filter_by(dept_name=current_user.dept_name).first()
            dept.reward_points += eve.reward_points
            db.session.commit()
            flash(f"Registration for {event_name} is successful.", "success")
            return redirect(url_for('main.profile'))
    else:
        flash(f"Only {event.team_size} participants can be there as limit was set by your Team Leader.", "info")
        return redirect(url_for('main.profile'))


@main.route('/payment_success/', methods=['POST'])
@login_required
def payment_success():
    event_id = request.form.get('event_id')
    eve = EventRegistration.query.filter_by(pay_id=event_id).first()
    pay = Payments.query.filter_by(payment_id=eve.pay_id).first()
    eve.paid = 1
    pay.status = "Success"
    db.session.commit()
    flash("Payment Received.", "success")
    return redirect(url_for('main.dashboard'))


@main.route('/gallery/')
def gallery():
    """Gallery Route"""
    return render_template('gallery.html')


@main.route('/dashboard/')
@login_required
def dashboard():
    """Dashboard Route"""
    if current_user.role != "Co-ordinator":
        return redirect(url_for('main.core_dashboard'))
    events_list = []
    event = Events.query.filter_by(main_co_ordinator=current_user.id).all()
    for eve in event:
        events_list.extend(EventRegistration.query.filter_by(event_name=eve.event_name).all())
    #events = EventRegistration.query.filter_by(event_name=event.event_name).all()
    total_found = len(events_list)
    total_amount = 0
    for event in events_list:
        total_amount += int(event.fees)
    return render_template('coordinator.html', events=events_list, total_found=total_found, total_amount=total_amount)


@main.route('/core_dashboard/')
@login_required
def core_dashboard():
    """Core Dashboard Route"""
    if current_user.role != "Core":
        return redirect(url_for('main.dashboard'))

    sports = len(EventRegistration.query.filter_by(event_type='sports').all())
    cultural = len(EventRegistration.query.filter_by(event_type='cultural').all())
    managerial = len(EventRegistration.query.filter_by(event_type='managerial').all())
    technical = len(EventRegistration.query.filter_by(event_type='technical').all())
    depts = Department.query.all()
    
    sports_eve = EventRegistration.query.filter_by(event_type="sports").all()
    cultural_eve = EventRegistration.query.filter_by(event_type="cultural").all()
    managerial_eve = EventRegistration.query.filter_by(event_type="managerial").all()
    technical_eve = EventRegistration.query.filter_by(event_type="technical").all()

    sports_amount = 0
    cultural_amount = 0
    managerial_amount = 0
    technical_amount = 0

    for event in sports_eve:
        sports_amount += int(event.fees)
    for event in cultural_eve:
        cultural_amount += int(event.fees)
    for event in managerial_eve:
        managerial_amount += int(event.fees)
    for event in technical_eve:
        technical_amount += int(event.fees)
    
    return render_template('dashboard.html', sports=sports, cultural=cultural, managerial=managerial, 
    technical=technical, depts=depts, sports_amount=sports_amount, cultural_amount=cultural_amount, managerial_amount=managerial_amount, technical_amount=technical_amount)


@main.route('/core_dashboard/<event_type>/')
@login_required
def event_wise_data(event_type):
    """Event-wise Route"""
    if current_user.role != "Core":
        return redirect(url_for('main.dashboard'))

    events = EventRegistration.query.filter_by(event_type=event_type).filter_by(paid=1).all()

    return render_template('core-committee.html', events=events, event_type=event_type)
