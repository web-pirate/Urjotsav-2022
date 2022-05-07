from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app 
from Urjotsav.main.forms import RequestResetForm, ResetPasswordForm
from Urjotsav.models import User, EventRegistration, Events, Department, Payments, Counter
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
    c = Counter.query.first()
    if not c:
       counter = Counter(count=4999)
       db.session.add(counter)
       db.session.commit()
    c = Counter.query.first()
    c.count += 1
    db.session.commit()
    return render_template('index.html', count=c.count)


@main.route('/about/')
def about():
  """About Route"""
  c = Counter.query.first()
  return render_template('about.html', count=c.count)


@main.route('/register/', methods=['GET', 'POST'])
def register():
    """Registration Route"""
    c = Counter.query.first()
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))
    if request.method == 'POST':
        if request.form.get('password') == request.form.get('cpassword'):
            if not User.query.filter_by(email=request.form.get('email').strip().lower()).first() and not User.query.filter_by(mobile_number=request.form.get('mobile_number')).first():
                s = URLSerializer(current_app.config['SECRET_KEY'])
                remember = request.form.get('remember')
                college = request.form.get('college')
                if not remember:
                    college = "Prestige Institute of Engineering Management & Research, Indore"
                token = s.dumps({"college": college, "name": request.form.get('name'), "email": request.form.get('email').strip().lower(), "Mobile Number": request.form.get('mobile_number'), "enrollment_number": request.form.get('enrollment_number'), "dept_name": request.form.get('dept_name'), "password": request.form.get('password')},
                                salt="send-email-confirmation")
                try:
                    send_confirm_email(email=request.form.get('email').strip().lower(), token=token)
                except Exception as e:
                    flash(f"{e}", "danger")
                    return redirect(url_for('main.login'))

                flash(f"An confirmation email has been sent to you on {request.form.get('email')}!", "success")
                return redirect(url_for('main.login'))
            else:
                flash(
                    f"You already have an account! Either Email or Mobile Number is already in use.", "info")
                return redirect(url_for('main.login'))
        else:
            flash(
                f"Please, check your password", "alert")
            return redirect(url_for('main.register'))
    return render_template('registration.html', count=c.count)

@main.route('/t&c/')
def tc():
    c = Counter.query.first()
    return render_template('t&c.html', count=c.count)

@main.route('/privacy/')
def privacy():
    c = Counter.query.first()
    return render_template('Privacy.html', count=c.count)

@main.route('/refund_policy/')
def refund():
    c = Counter.query.first()
    return render_template('refund.html', count=c.count)

# ------ Confirm Registration ------ #
@main.route('/confirm_email/<token>/')
def confirm_email(token):
    s = URLSerializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token, salt="send-email-confirmation", max_age=600)
        is_piemr = False
        if data['email'].lower().strip().split('@')[-1] == 'piemr.edu.in':
            is_piemr = True
        user = User(name=data['name'], college=data['college'], enrollment_number=data["enrollment_number"], email=data["email"].strip(), mobile_number=data['Mobile Number'], password=data["password"], 
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
    c = Counter.query.first()
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password.", "info")
        return redirect(url_for('main.login'))
    return render_template('reset_request.html', form=form, count=c.count)


# ------ Reset Password <TOKEN> Route ------ #
@main.route('/reset_password/<token>/', methods=['GET', 'POST'])
def reset_token(token):
    c = Counter.query.first()
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
    return render_template('reset_token.html', form=form, count=c.count)


@main.route('/login/', methods=['GET', 'POST'])
def login():
    """Login Route"""
    c = Counter.query.first()
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
                flash("Please check your password. Password don't match!", "danger")
                return redirect(url_for('main.login'))
        else:
            flash(
                "You don't have an account. Please create now to login.", "info")
            return redirect(url_for('main.register'))
    return render_template('login.html', count=c.count)


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
    c = Counter.query.first()
    if current_user.role != "Student":
        return redirect(url_for('main.dashboard'))
    total_amount = 0
    events = EventRegistration.query.filter_by(user_id=current_user.id).all()
    for event in events:
        total_amount += int(event.fees.replace(' / Team', ''))
    return render_template('profile.html', events=events, total_amount=total_amount, count=c.count)


@main.route('/event/<event_type>/')
def event(event_type):
    """All Event Route"""
    c = Counter.query.first()
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
    return render_template('event.html', events=events, current_event=current_event, count=c.count)


@main.route('/event_registration/<event_name>/', methods=['GET', 'POST'])
@login_required
def event_registration(event_name):
    """Event Registration"""
    c = Counter.query.first()
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
            pay_status = "Processing"
            paid_status = 0
            if fees == '0':
                pay_status = "Success"
                paid_status = 1
            pay_id = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=25))
            pay = Payments(amount=fees, payment_id=pay_id, date=datetime.now(tz), status=pay_status, user_id=current_user.id)
            eve = EventRegistration(event_type=event_type, event_name=event_name, fees=fees, date=date, venue=venue, 
            team_size=team_size, team_members=current_user.name, team_members_id=current_user.id, paid=paid_status, team_leader=current_user.name, pay_id=pay_id, mobile_number=current_user.mobile_number, 
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
            send_event_registration_link_co_ordinator(email=user.email, event_name=event_name, team_leader=current_user.name)
            flash(f"{message}", "success")
            flash(f"Please contact your co-ordinator {user.name.title()} on {user.mobile_number} for making Payment.", "info")
            return redirect(url_for('main.profile'))
        flash("You already registered for this event.", "info")
        return redirect(url_for('main.profile'))
    return render_template('event_register.html', event_name=event_name, count=c.count)


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


@main.route('/reward_point_add/', methods=['POST'])
@login_required
def reward_point_add():
    event_id = request.form.get('event_id')
    position = request.form.get('position')
    eve = EventRegistration.query.filter_by(pay_id=event_id).first()
    events = EventRegistration.query.filter_by(event_name=eve.event_name).all()
    team_members = eve.team_members_id.split(', ')
    for member in team_members:
        user = User.query.filter_by(id=int(member)).first()
        dept = Department.query.filter_by(dept_name=user.dept_name).first()
        message = ""
        points = 0
        if position == "first":
            points = 25
            message = "First Position allocated."
        else:
            points = 10
            message = "Second Position allocated."
        user.reward_points += points
        dept.reward_points += points
        db.session.commit()
    if position == 'first':
        for event in events:
            event.first_no = False
            db.session.commit()
    else:
        for event in events:
            event.second_no = False
            db.session.commit()

    flash(message, "success")
    return redirect(url_for('main.dashboard'))


@main.route('/event_delete/', methods=['POST'])
@login_required
def event_delete():
    event_id = request.form.get('event_id')
    eve = EventRegistration.query.filter_by(pay_id=event_id).first()
    pay = Payments.query.filter_by(payment_id=event_id).first()
    event = Events.query.filter_by(event_name=eve.event_name).first()
    members = eve.team_members_id.split(', ')
    for member in members:
        user = User.query.filter_by(id=int(member)).first()
        user.reward_points -= event.reward_points
        dept = Department.query.filter_by(dept_name=user.dept_name).first()
        dept.reward_points -= event.reward_points
        db.session.commit()
    db.session.delete(eve)
    db.session.delete(pay)
    db.session.commit()
    flash("Deleted successfully.", "success")
    return redirect(url_for('main.dashboard'))



@main.route('/gallery/')
def gallery():
    """Gallery Route"""
    c = Counter.query.first()
    return render_template('gallery.html', count=c.count)



@main.route('/dashboard/')
@login_required
def dashboard():
    """Dashboard Route"""
    c = Counter.query.first()
    if current_user.role != "Co-ordinator":
        return redirect(url_for('main.core_dashboard'))
    events_list = []
    event_list_collected = []
    event = Events.query.filter_by(main_co_ordinator=current_user.id).all()
    for eve in event:
        events_list.extend(EventRegistration.query.filter_by(event_name=eve.event_name).all())
    for eve in event:
        event_list_collected.extend(EventRegistration.query.filter_by(event_name=eve.event_name).filter_by(paid=1).all())
    total_found = len(events_list)
    total_amount = 0
    total_amount_collected = 0
    for eve in events_list:
        total_amount += int(eve.fees.replace(' / Team', ''))
    for eve in event_list_collected:
        total_amount_collected += int(eve.fees.replace(' / Team', ''))
    return render_template('coordinator.html', events=events_list, total_found=total_found, total_amount=total_amount, event=event, count=c.count, total_amount_collected=total_amount_collected)


@main.route('/core_dashboard/', methods=['GET', 'POST'])
@login_required
def core_dashboard():
    """Core Dashboard Route"""
    c = Counter.query.first()
    if current_user.role != "Core":
        return redirect(url_for('main.dashboard'))

    sports = len(EventRegistration.query.filter_by(event_type='sports').all())
    cultural = len(EventRegistration.query.filter_by(event_type='cultural').all())
    managerial = len(EventRegistration.query.filter_by(event_type='managerial').all())
    technical = len(EventRegistration.query.filter_by(event_type='technical').all())
    depts = Department.query.order_by(Department.reward_points.desc()).all()

    sports_eve = EventRegistration.query.filter_by(event_type="sports").all()
    cultural_eve = EventRegistration.query.filter_by(event_type="cultural").all()
    managerial_eve = EventRegistration.query.filter_by(event_type="managerial").all()
    technical_eve = EventRegistration.query.filter_by(event_type="technical").all()

    sports_eve_collected = EventRegistration.query.filter_by(event_type="sports").filter_by(paid=1).all()
    cultural_eve_collected = EventRegistration.query.filter_by(event_type="cultural").filter_by(paid=1).all()
    managerial_eve_collected = EventRegistration.query.filter_by(event_type="managerial").filter_by(paid=1).all()
    technical_eve_collected = EventRegistration.query.filter_by(event_type="technical").filter_by(paid=1).all()
    users = User.query.order_by(User.reward_points.desc()).all()[0:3]
    get_range = "Top 3"

    sports_amount = 0
    cultural_amount = 0
    managerial_amount = 0
    technical_amount = 0

    sports_amount_collected = 0
    cultural_amount_collected = 0
    managerial_amount_collected = 0
    technical_amount_collected = 0

    for event in sports_eve:
        sports_amount += int(event.fees.replace(' / Team', ''))
    for event in cultural_eve:
        cultural_amount += int(event.fees.replace(' / Team', ''))
    for event in managerial_eve:
        managerial_amount += int(event.fees.replace(' / Team', ''))
    for event in technical_eve:
        technical_amount += int(event.fees.replace(' / Team', ''))

    for event in sports_eve_collected:
        sports_amount_collected += int(event.fees.replace(' / Team', ''))
    for event in cultural_eve_collected:
        cultural_amount_collected += int(event.fees.replace(' / Team', ''))
    for event in managerial_eve_collected:
        managerial_amount_collected += int(event.fees.replace(' / Team', ''))
    for event in technical_eve_collected:
        technical_amount_collected += int(event.fees.replace(' / Team', ''))

    if request.method == "POST":
        get_range = int(request.form.get('get_range'))
        users = User.query.filter(User.reward_points>=int(request.form.get('get_range'))).order_by(User.reward_points.desc()).all()

    return render_template('dashboard.html', sports=sports, cultural=cultural, users=users,
     managerial=managerial, technical=technical, depts=depts, technical_amount_collected=technical_amount_collected,
     managerial_amount_collected=managerial_amount_collected, sports_amount=sports_amount, sports_amount_collected=sports_amount_collected,
     cultural_amount_collected=cultural_amount_collected, cultural_amount=cultural_amount, managerial_amount=managerial_amount,
     technical_amount=technical_amount, count=c.count, get_range=get_range)


@main.route('/core_dashboard/<event_type>/')
@login_required
def event_wise_data(event_type):
    """Event-wise Route"""
    c = Counter.query.first()
    if current_user.role != "Core":
        return redirect(url_for('main.dashboard'))
    total_event = set()
    events_list = list()
    events = EventRegistration.query.filter_by(event_type=event_type).filter_by(paid=1).all()

    for event in events:
        total_event.add(event.event_name)

    for eve in total_event:
        fees = 0
        even = EventRegistration.query.filter_by(event_name=eve).filter_by(paid=1).all()
        for eve_paid in even:
            fees += int(eve_paid.fees.replace(' / Team', ''))
        dic = {"event_name": eve, "total_registration": len(even), "fees": fees}
        events_list.append(dic)
    return render_template('core-committee.html', events=events, event_type=event_type, events_list=events_list, count=c.count)

@main.route('/core_dashboard/<event_type>/<event_name>/')
@login_required
def event_wise_user(event_type, event_name):
    c = Counter.query.first()
    events = EventRegistration.query.filter_by(event_type=event_type).filter_by(event_name=event_name).filter_by(paid=1).all()
    event = Events.query.filter_by(event_type=event_type).filter_by(event_name=event_name).first()
    event_date = event.event_date
    in_event_fees = event.in_entry_fees
    out_event_fees = event.out_entry_fees
    return render_template('event_wise_user.html', events=events, event_name=event_name, event_date=event_date, 
    in_event_fees=in_event_fees, out_event_fees=out_event_fees, count=c.count)
