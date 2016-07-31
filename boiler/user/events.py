from boiler.events import Namespace

events = Namespace()

# -----------------------------------------------------------------------------
# User events
# -----------------------------------------------------------------------------

# persist
user_save_event = events.signal(
    'user_saved',
    'Sent when user entity is persisted'
)

# remove
user_delete_event = events.signal(
    'user_deleted',
    'Sent when user entity is persisted'
)

# register
register_event = events.signal(
    'register',
    'Sent when user first registers'
)

# email update
email_update_requested_event = events.signal(
    'email_updated_requested',
    'Sent when user requested and email update'
)

email_confirmed_event = events.signal(
    'email_confirmed',
    'Sent when user confirms email address ownership'
)

# password change
password_change_requested_event = events.signal(
    'user_password_change_requested',
    'Sent when user requests password change'
)
password_changed_event = events.signal(
    'user_password_changed',
    'Sent when user changes password'
)

# login
login_event = events.signal(
    'login',
    'Sent when user logs in'
)

# login failed
login_failed_event = events.signal(
    'login_failed',
    'Sent when user fails to login.'
)

# login failed
login_failed_nonexistent_event = events.signal(
    'login_nonexistent',
    'Sent when user fails to login.'
)

# logout
logout_event = events.signal(
    'logout',
    'Sent when user logs out'
)

# role added
user_got_role_event = events.signal(
    'user_got_role',
    'Sent when user gets new role'
)

# role removed
user_lost_role_event = events.signal(
    'user_lost_role',
    'Sent when user gets a role removed'
)


# -----------------------------------------------------------------------------
# Role event
# -----------------------------------------------------------------------------

role_saved_event = events.signal(
    'role_saved',
    'Sent when a role is updated'
)

role_created_event = events.signal(
    'role_created',
    'Sent when a role is first created'
)

role_deleted_event = events.signal(
    'role_deleted',
    'Sent when a role is deleted'
)