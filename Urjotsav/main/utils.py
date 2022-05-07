from Urjotsav import mail
from flask_mail import Message
from flask import url_for


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=('URJOTSAV 2K22', '51110102966@piemr.edu.in'), recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link. The link will expire in 10 minutes:
{url_for('main.reset_token', token=token, _external=True)}

If your did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


def send_confirm_email(email, token):
    msg = Message('Confirm Your Account',
                  sender=('URJOTSAV 2K22', '51110102966@piemr.edu.in'), recipients=[email])
    msg.body = f'''To confirm your email, visit the following link. The link will expire in 10 minutes:
{url_for('main.confirm_email', token=token, _external=True)}

'''
    mail.send(msg)

def send_event_registration_link(email, event_name, team_leader, pay_id):
    msg = Message(f'Link for {event_name} Team Registration',
                  sender=('URJOTSAV 2K22', '51110102966@piemr.edu.in'), recipients=[email])
    msg.body = f'''Share This Link With Your Team Members. Team members must register on Official website first. You don't need to click on it.:
{url_for('main.event_registration_team_members', event_name=event_name, team_leader=team_leader, pay_id=pay_id, _external=True)}
'''
    mail.send(msg)


def send_event_registration_link_co_ordinator(email, event_name, team_leader):
    msg = Message(f'Team Registration for {event_name}',
                  sender=('URJOTSAV 2K22', '51110102966@piemr.edu.in'), recipients=[email])
    msg.body = f'''Event Name: {event_name}
Team Leader: {team_leader}
'''
    mail.send(msg)
