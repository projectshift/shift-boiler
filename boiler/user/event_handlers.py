from flask import current_app
from boiler.user import events

"""
Event handlers
A collection of default handlers for events emitted in user service.
"""

# -----------------------------------------------------------------------------
# User events
# -----------------------------------------------------------------------------


def user_save_event(user):
    """ Handle persist event for user entities """
    msg = 'User ({}){} updated/saved'.format(user.id, user.email)
    current_app.logger.info(msg)
    # doggy.increment('user.updated')


def user_delete_event(user):
    """ Handle delete event for user entities """
    msg = 'User ({}){} deleted'.format(user.id, user.email)
    current_app.logger.info(msg)
    # doggy.increment('user.deleted')


def login_event(user):
    """ Handle login event """
    msg = 'User ({}){} logged in'.format(user.id, user.email)
    current_app.logger.info(msg)
    # doggy.increment('user.login')


def login_nonexistent_event(user):
    """ Handle login nonexistent user event """
    msg = 'Login failed for nonexistent user'
    current_app.logger.info(msg)
    # doggy.increment('user.login.failed.nonexistent')
    # doggy.increment('user.login.failed')


def login_failed_event(user):
    """ Handle login nonexistent user event """
    msg = 'Login failed for user ({}){}'.format(user.id, user.email)
    current_app.logger.info(msg)
    # doggy.increment('user.login.failed')


def logout_event(user):
    """ Handle logout event """
    msg = 'User ({}){} logged out'.format(user.id, user.email)
    current_app.logger.info(msg)
    # doggy.increment('user.logout')


def register_event(user):
    """ Handle registration event """
    msg = 'User ({}){} registered'.format(user.id, user.email)
    current_app.logger.info(msg)
    # doggy.increment('user.registered')


def email_update_requested_event(user):
    """ Handle email updated request event """
    msg = 'User ({}){} requested email update'.format(user.id, user.email)
    current_app.logger.info(msg)


def email_confirmed_event(user):
    """ Handle email confirmed event """
    msg = 'User ({}){} confirmed email'.format(user.id, user.email)
    current_app.logger.info(msg)
    # doggy.increment('user.email_confirmed')


def password_change_requested_event(user):
    """ Request password change event"""
    msg = 'User ({}){} requested password change'.format(user.id, user.email)
    current_app.logger.info(msg)
    # doggy.increment('user.password_change_requested')


def password_changed_event(user):
    """ Handle password changed event """
    msg = 'User ({}){} changed password'.format(user.id, user.email)
    current_app.logger.info(msg)
    # doggy.increment('user.password_changed')


events.user_save_event.connect(user_save_event)
events.user_delete_event.connect(user_delete_event)
events.login_event.connect(login_event)
events.login_failed_nonexistent_event.connect(login_nonexistent_event)
events.login_failed_event.connect(login_failed_event)
events.logout_event.connect(logout_event)
events.register_event.connect(register_event)
events.email_update_requested_event.connect(email_update_requested_event)
events.password_change_requested_event.connect(password_change_requested_event)
events.password_changed_event.connect(password_changed_event)

# -----------------------------------------------------------------------------
# Role events
# -----------------------------------------------------------------------------


def user_got_role_event(user, role):
    """ User got new role """
    msg = 'User ({}){} got new role [{}]'
    current_app.logger.info(msg.format(user.id, user.email, role.handle))


def user_lost_role_event(user, role):
    """ User lost a role """
    msg = 'User ({}){} lost a role [{}]'
    current_app.logger.info(msg.format(user.id, user.email, role.handle))

events.user_got_role_event.connect(user_got_role_event)
events.user_lost_role_event.connect(user_lost_role_event)
