from unittest import mock
from nose.plugins.attrib import attr
from tests.base_testcase import BoilerTestCase

import jwt
from datetime import datetime, timedelta
from flask import session
from shiftschema.result import Result

from boiler.feature.mail import mail
from boiler.user.services import user_service, role_service
from boiler.user import events, exceptions as x
from boiler.user.events import events as user_events
from boiler.user.models import User, Role
from boiler.user.user_service import UserService
from boiler.config import DefaultConfig
from boiler import bootstrap


def custom_token_implementation(user_id):
    """ Custom JWT implementation """
    return 'CUSTOM TOKEN FOR [{}]'.format(user_id)

def custom_token_loader(token):
    """ Custom JWT token user loader implementation """
    return 'LOADED USER FROM TOKEN [{}]'.format(token)

@attr('user', 'service')
class UserServiceTests(BoilerTestCase):

    def setUp(self):
        super().setUp()
        self.create_db()

    def create_user(self, confirm_email=True):
        """ A shortcut to quickly create and return a user """
        with user_events.disconnect_receivers():
            user = user_service.create(
                email='test@test.com',
                password='123456'
            )
            if confirm_email:
                user.confirm_email()
            user_service.save(user)

        return user

    # ------------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------------

    def test_instantiate(self):
        """ Creating user service """
        service = UserService()
        self.assertIsInstance(service, UserService)

    def test_can_initialise_from_a_flask_app(self):
        """ Initialising user service from a flask app """
        service = UserService()
        self.assertEquals(0, len(service.email_subjects.keys()))

        service.init(self.app)
        self.assertNotEquals(0, len(service.email_subjects.keys()))
        self.assertEquals(
            self.app.config.get('USER_EMAIL_SUBJECTS'),
            service.email_subjects
        )

    def test_save(self):
        """ Persisting user """
        user = User(email='test@test.com', password='123')
        with user_events.disconnect_receivers():
            user_service.save(user)
        self.assertEqual(1, user.id)

    def test_save_emits_event(self):
        """ Saving a user emits event """
        user = User(email='test@test.com', password='123')
        with user_events.disconnect_receivers():
            spy = mock.Mock()
            events.user_save_event.connect(spy, weak=False)
            user_service.save(user)
            spy.assert_called_with(user)

    def test_save_returns_validation_errors(self):
        """ Saving returns validation error on bad data """
        result = user_service.save(User())
        self.assertFalse(result)
        self.assertIsInstance(result, Result)

    def test_delete(self):
        """ Deleting a user"""
        user = self.create_user()
        id = user.id
        with user_events.disconnect_receivers():
            user_service.delete(user)
            self.assertIsNone(user_service.get(id))

    def test_delete_emits_event(self):
        """ Deleting a user emits event """
        user = self.create_user()
        with user_events.disconnect_receivers():
            event = events.user_delete_event
            spy = mock.Mock()
            event.connect(spy, weak=False)
            user_service.delete(user)
            spy.assert_called_with(user)

    # ------------------------------------------------------------------------
    # Login and logout
    # ------------------------------------------------------------------------

    def test_login_successful_with_valid_credentials(self):
        """ Can login with valid credentials """
        user = self.create_user()
        with user_events.disconnect_receivers():
            with self.app.test_request_context():
                res = user_service.login(user.email, '123456')
                self.assertTrue(res)
                self.assertTrue('user_id' in session)

    def test_force_login(self):
        """ Can force login a user """
        user = self.create_user()
        with user_events.disconnect_receivers():
            with self.app.test_request_context():
                res = user_service.force_login(user)
                self.assertTrue(res)
                self.assertTrue('user_id' in session)

    def test_force_login_emits_event(self):
        """ Force login emits event """
        user = self.create_user()
        with user_events.disconnect_receivers():
            with self.app.test_request_context():
                spy = mock.Mock()
                events.login_event.connect(spy, weak=False)
                user_service.login(user.email, '123456')
                spy.assert_called_with(user)

    def test_login_fails_with_bad_credentials(self):
        """ Fail to login with bad credentials """
        with user_events.disconnect_receivers():
            with self.app.test_request_context():
                email = 'no-such-email'
                password = 'whatever'
                res = user_service.login(email, password)
                self.assertFalse(res)

    def test_login_emits_event_on_success(self):
        """ Login emits event on success """
        user = self.create_user()
        event = events.login_event
        with user_events.disconnect_receivers():
            spy = mock.Mock()
            event.connect(spy, weak=False)
            with self.app.test_request_context():
                user_service.login(user.email, '123456')
            spy.assert_called_with(user)

    def test_login_emits_event_on_bad_credentials(self):
        """ Login emits event on bad credentials"""
        user = self.create_user()
        event = events.login_failed_event
        with user_events.disconnect_receivers():
            spy = mock.Mock()
            event.connect(spy, weak=False)  # weak please
            with self.app.test_request_context():
                user_service.login(user.email, 'BAD!')
            spy.assert_called_with(user)

    def test_login_emit_event_on_nonexistent_user(self):
        """ Login emits event on nonexistent user login """
        event = events.login_failed_nonexistent_event
        with user_events.disconnect_receivers():
            spy = mock.Mock()
            event.connect(spy, weak=False)  # weak please
            with self.app.test_request_context():
                user_service.login('NONEXISTENT', 'BAD!')
            spy.assert_called_with(None)

    def test_logout(self):
        """ Can logout """
        user = self.create_user()
        with user_events.disconnect_receivers():
            with self.app.test_request_context():
                result = user_service.login(user.email, '123456')
                self.assertTrue(result)  # login first
                self.assertTrue('user_id' in session)
                result = user_service.logout()  # now logout
                self.assertTrue(result)
                self.assertFalse('user_id' in session)

    def test_logout_emits_event(self):
        """ Logout emits event """
        user = self.create_user()
        event = events.logout_event
        with user_events.disconnect_receivers():
            spy = mock.Mock()
            event.connect(spy, weak=False)  # weak please
            with self.app.test_request_context():
                result = user_service.login(user.email, '123456')
                self.assertTrue(result)  # login first
                result = user_service.logout()  # now logout
                self.assertTrue(result)

            current_user = None  # None, since mocked
            spy.assert_called_with(current_user)

    def test_attempts_social_login(self):
        """ Attempting login with social user profile """
        user = self.create_user()
        with user_events.disconnect_receivers():
            facebook_id = '123456790'
            user.facebook_id = facebook_id
            user_service.save(user)

            self.assertFalse(user_service.attempt_social_login(
                'facebook',
                facebook_id + 'BAD'
            ))

            with self.app.test_request_context():
                self.assertTrue(user_service.attempt_social_login(
                    'facebook',
                    facebook_id
                ))

    # -------------------------------------------------------------------------
    # Account locks and counting bad logins
    # -------------------------------------------------------------------------

    def test_login_increments_on_failure(self):
        """ Increment failed logins counter on failure """
        user = self.create_user()
        self.assertEqual(0, user.failed_logins)
        with user_events.disconnect_receivers():
            with self.app.test_request_context():
                user_service.login(user.email, 'BAD!')
                self.assertEqual(1, user.failed_logins)

    def test_login_locks_on_reaching_limit(self):
        """ Lock account on reaching failed logins limit """
        with user_events.disconnect_receivers():
            user = self.create_user()
            user.failed_logins = 10
            user_service.save(user)
            with self.app.test_request_context():
                user_service.login(user.email, 'BAD!')
                self.assertEqual(0, user.failed_logins)
                self.assertTrue(user.is_locked())

    def test_login_fails_if_locked(self):
        """ Abort login if account locked """
        with user_events.disconnect_receivers():
            user = self.create_user()
            user.lock_account()
            user_service.save(user)
            with self.app.test_request_context():
                with self.assertRaises(x.AccountLocked):
                    user_service.login(user.email, 'BAD!')

    def test_login_fails_if_email_unconfirmed_for_new_users(self):
        """ Abort login if email is not confirmed for new users"""
        with user_events.disconnect_receivers():
            user = self.create_user(False)
            with self.app.test_request_context():
                with self.assertRaises(x.EmailNotConfirmed):
                    user_service.login(user.email, 'BAD!')

    def test_login_possible_if_email_unconfirmed_for_existing_users(self):
        """ Login possible if email is not confirmed for existing users"""
        with user_events.disconnect_receivers():
            user = self.create_user()
            with self.app.test_request_context():
                user_service.login(user.email, 'BAD!')

    def test_login_drops_counter_on_success(self):
        """ Drop failed login counter on success """
        with user_events.disconnect_receivers():
            user = self.create_user()
            user.failed_logins = 5
            user_service.save(user)
            with self.app.test_request_context():
                user_service.login(user.email, '123456')
                self.assertEqual(0, user.failed_logins)

    def test_force_login_fails_if_locked(self):
        """ Abort force login if locked """
        with user_events.disconnect_receivers():
            user = self.create_user()
            user.lock_account()
            user_service.save(user)
            with self.app.test_request_context():
                with self.assertRaises(x.AccountLocked):
                    user_service.force_login(user)

    def test_force_login_fails_if_email_unconfirmed_for_new_users(self):
        """ Abort force login if email is not confirmed for new users"""
        with user_events.disconnect_receivers():
            user = self.create_user(False)
            with self.app.test_request_context():
                with self.assertRaises(x.EmailNotConfirmed):
                    user_service.force_login(user)

    def test_force_login_doesnt_fail_if_email_unconfirmed_for_existing(self):
        """ Force login for existing users with unconfirmed email """
        with user_events.disconnect_receivers():
            user = self.create_user()
            with self.app.test_request_context():
                user_service.force_login(user)

    def test_force_login_drops_counter_on_success(self):
        """ Drop failed login counter on force login """
        with user_events.disconnect_receivers():
            user = self.create_user()
            user.failed_logins = 5
            user_service.save(user)
            with self.app.test_request_context():
                user_service.force_login(user)
                self.assertEqual(0, user.failed_logins)

    # -------------------------------------------------------------------------
    # Register and welcome message
    # -------------------------------------------------------------------------

    def test_register_returns_validation_errors(self):
        """ Registering returns validation error on bad data """
        with user_events.disconnect_receivers():
            user_data = dict(
                email='not.email',
                password='123'
            )
            result = user_service.register(
                user_data=user_data,
                send_welcome=False
            )
            self.assertIsInstance(result, Result)
            self.assertFalse(result)

    def test_register(self):
        """ Can register new user """
        with user_events.disconnect_receivers():
            user_data = dict(email='test@test.com', password='123')
            user = user_service.register(
                user_data=user_data,
                send_welcome=False
            )
            self.assertIsInstance(user, User)
            self.assertEqual(1, user.id)

    def test_register_password_can_be_verified(self):
        """ REGRESSION: Password provided at registration can be verified """
        user_data = dict(email='tester@test.com', password='111111')
        with user_events.disconnect_receivers():
            user = user_service.register(
                user_data=user_data,
                send_welcome = False
            )

        verified = user.verify_password(user_data['password'])
        self.assertTrue(verified)

        password = 222222
        user.password = password
        user_service.save(user)
        verified = user.verify_password(password)
        self.assertTrue(verified)

    def test_register_emits_event(self):
        """ Registration emits event """
        event = events.register_event
        user_data = dict(email='test@test.com', password='123')
        with user_events.disconnect_receivers():
            spy = mock.Mock()
            event.connect(spy, weak=False)
            user = user_service.register(
                user_data=user_data,
                send_welcome=False
            )
            spy.assert_called_with(user)

    def test_register_send_welcome_message(self):
        """ Registration sends welcome message"""
        user_data = dict(email='test@test.com', password='123')
        with mail.record_messages() as out:
            user_service.register(user_data=user_data)
        self.assertEquals(1, len(out))

    def test_account_confirmation_message_send(self):
        """ Account confirmation message can be sent """
        user = User(email='test@test.com', password='123')
        with mail.record_messages() as out:
            with self.app.test_request_context():
                url = 'http://my.confirm.url/'
                user_service.require_confirmation = True
                user_service.send_welcome_message(user, url)

            msg = out[0]
            self.assertTrue('Confirm email' in msg.html)
            self.assertTrue('Confirm email' in msg.body)
            self.assertTrue(user.email_link in msg.html)
            self.assertTrue(user.email_link in msg.body)

    def test_account_confirmation_message_resend(self):
        """ Account confirmation message can be resent """
        user_data = dict(email='tester@test.com', password='123456')
        with events.events.disconnect_receivers():
            with self.app.test_request_context():
                user_service.require_confirmation = True
                u = user_service.register(
                    user_data=user_data,
                    send_welcome=False
                )
                initial_link = u.email_link
                with mail.record_messages() as out:
                    url = 'http://my.confirm.url/'
                    user_service.resend_welcome_message(u, url)
                    resend_link = u.email_link
                    self.assertNotEqual(initial_link, resend_link)

                    msg = out[0]
                    self.assertTrue('Confirm email' in msg.html)
                    self.assertTrue('Confirm email' in msg.body)

    # -------------------------------------------------------------------------
    # Confirm email (both welcome and email change)
    # -------------------------------------------------------------------------

    def test_email_confirm_fails_with_bad_link(self):
        """ Fail to initially confirm email with bad link  """
        link = 'no-such-link'
        self.assertFalse(user_service.confirm_email_with_link(link))

    def test_email_confirm_raises_on_expired_link(self):
        """ Raise if initially confirming with expired link """
        user = self.create_user()
        with events.events.disconnect_receivers():
            user.email = 'updated@test.com'
            user.email_link_expires = datetime.utcnow() - timedelta(hours=12)
            self.assertFalse(user.email_confirmed)
            user_service.save(user)
        with self.assertRaises(x.EmailLinkExpired):
            user_service.confirm_email_with_link(user.email_link)

    def test_email_confirm_possible(self):
        """ Doing initial email confirmation"""
        user = self.create_user()
        with events.events.disconnect_receivers():
            user.email = 'updated@test.com'
            user_service.save(user)
            res = user_service.confirm_email_with_link(user.email_link)
            self.assertTrue(res)

        self.assertTrue(user.email_confirmed)
        self.assertIsNone(user.email_link)

    def test_email_confirm_emits_event(self):
        """ Initial email confirmation emits event """
        user = self.create_user()
        with events.events.disconnect_receivers():
            user.email = 'updated@test.com'
            spy = mock.Mock()
            events.email_confirmed_event.connect(spy, weak=False)
            user_service.save(user)
            user_service.confirm_email_with_link(user.email_link)
            spy.assert_called_with(user)

    # -------------------------------------------------------------------------
    # Change email and confirmation
    # -------------------------------------------------------------------------

    def test_change_email_returns_validation_errors(self):
        """ Change email returns validation errors on bad data """
        u = User(email='ok@ok.com', password='123')
        with events.events.disconnect_receivers():
            res = user_service.change_email(
                u,
                'not-an-email',
                send_message=False
            )
            self.assertIsInstance(res, Result)

    def test_change_email_possible(self):
        """ Email change procedure is possible"""
        with events.events.disconnect_receivers():
            with self.app.test_request_context():
                u = self.create_user()
                user_service.force_login(u)
                self.assertTrue('user_id' in session)

                res = user_service.change_email(
                    u,
                    'new@email.com',
                    send_message=False
                )
                self.assertIsInstance(res, User)
                self.assertEqual('new@email.com', u.email_new)
                self.assertIsNotNone(u.email_link)

                # do not log out
                self.assertTrue('user_id' in session)

    def test_change_email_emits_event(self):
        """ Email change request emits event"""
        with events.events.disconnect_receivers():
            with self.app.test_request_context():
                u = self.create_user()
                spy = mock.Mock()
                events.email_update_requested_event.connect(spy, weak=False)
                user_service.change_email(
                    u,
                    'new@email.com',
                    send_message=False
                )
                spy.assert_called_with(u)

    def test_changing_email_sends_email(self):
        """ Send email message with confirmation link when changing email"""
        with events.events.disconnect_receivers():
            with mail.record_messages() as out:
                with self.app.test_request_context():
                    u = self.create_user()
                    user_service.force_login(u)
                    self.assertTrue('user_id' in session)
                    res = user_service.change_email(u, 'new@email.com')
                    self.assertIsInstance(res, User)
                    self.assertEqual('new@email.com', u.email_new)
                    self.assertIsNotNone(u.email_link)
                    self.assertEquals(1, len(out))

            # regression: ensure email sent to **new** email not the current one
            self.assertEquals(1, len(out[0].recipients))
            self.assertIn(u.email_new, out[0].recipients)

    def test_change_email_message_send(self):
        """ Email change confirmation message can be sent"""
        with events.events.disconnect_receivers():
            user = self.create_user()
            user.email = 'updated@test.com'
            self.assertFalse(user.email_confirmed)
            with mail.record_messages() as out:
                with self.app.test_request_context():
                    url = 'http://my.confirm.url/'
                    user_service.send_email_changed_message(user, url)
                    msg = out[0]
                    self.assertTrue('confirm email' in msg.html.lower())
                    self.assertTrue('confirm email' in msg.body.lower())
                    self.assertTrue(user.email_link in msg.html)
                    self.assertTrue(user.email_link in msg.body)

    def test_change_email_message_resend(self):
        """ Email change confirmation message can be resent"""
        with events.events.disconnect_receivers():
            with mail.record_messages() as out:
                u = self.create_user()
                u.email = 'updated@test.com'
                initial_link = u.email_link
                url = 'http://my.confirm.url/'
                user_service.resend_email_changed_message(u, url)
                new_link = u.email_link
                self.assertNotEqual(initial_link, new_link)  # regenerated
                self.assertTrue('confirm email' in out[0].html.lower())
                self.assertTrue('confirm email' in out[0].body.lower())
                self.assertTrue(new_link in out[0].html)
                self.assertTrue(new_link in out[0].body)

    # -------------------------------------------------------------------------
    # Change password and confirmation
    # -------------------------------------------------------------------------

    def test_password_change_returns_validation_errors(self):
        """ Password change returns validation errors on bad data """
        u = self.create_user()
        u.email = '1'  # trigger error
        with events.events.disconnect_receivers():
            res = user_service.change_password(u, '0987654')
            self.assertIsInstance(res, Result)

    def test_password_change(self):
        """ Password change possible """
        u = self.create_user()
        with events.events.disconnect_receivers():
            with self.app.test_request_context():
                user_service.force_login(u)
                self.assertTrue('user_id' in session)
                user_service.change_password(u, '0987654')
                self.assertFalse('user_id' in session)
                self.assertTrue(u.verify_password('0987654'))

    def test_password_change_emits_event(self):
        """ Password change  """
        u = self.create_user()
        with events.events.disconnect_receivers():
            spy = mock.Mock()
            events.password_changed_event.connect(spy, weak=False)
            with self.app.test_request_context():
                user_service.force_login(u)
                self.assertTrue('user_id' in session)
                user_service.change_password(u, '0987654')
                self.assertFalse('user_id' in session)
                self.assertTrue(u.verify_password('0987654'))
                spy.assert_called_with(u)

    def test_send_password_message(self):
        """ Sending confirmation message to change password """
        with events.events.disconnect_receivers():
            user = self.create_user()
            user.generate_password_link()
            user_service.save(user)
            with mail.record_messages() as out:
                with self.app.test_request_context():
                    url = 'http://my.confirm.url/'
                    user_service.send_password_change_message(user, url)
                    msg = out[0]
                    self.assertTrue('change your password' in msg.html.lower())
                    self.assertTrue('change your password' in msg.body.lower())
                    self.assertTrue(user.password_link in msg.html)
                    self.assertTrue(user.password_link in msg.body)

    def test_request_password_reset(self):
        """ Request password reset generates a link and sends message """
        with events.events.disconnect_receivers():
            with mail.record_messages() as out:
                with self.app.test_request_context():
                    user = self.create_user()
                    url = 'http://my.confirm.url/'
                    user_service.request_password_reset(user, url)
                    self.assertTrue(type(user.password_link) is str)
                    self.assertEqual(1, len(out))

    def test_request_password_reset_emits_event(self):
        """ Requesting password reset emits event """
        with events.events.disconnect_receivers():
            with mail.record_messages() as out:
                with self.app.test_request_context():
                    user = self.create_user()
                    url = 'http://my.confirm.url/'
                    spy = mock.Mock()
                    events.password_change_requested_event.connect(
                        spy, weak=False
                    )
                    user_service.request_password_reset(user, url)
                    spy.assert_called_with(user)

    def test_can_add_role_to_user(self):
        """ Adding role to user """
        with events.events.disconnect_receivers():
            user = self.create_user()
            role = Role(handle='test_role', title='Testing')
            ok = role_service.save(role)
            if not ok:
                self.fail('Role invalid')

            user_service.add_role_to_user(user, role)
            self.assertTrue(user.has_role(role))

    def test_adding_role_emits_event(self):
        """ Adding role to user emits event """
        with user_events.disconnect_receivers():
            user = self.create_user()
            role = Role(handle='test_role', title='Testing')
            role_service.save(role, user)

            spy = mock.Mock()
            events.user_got_role_event.connect(spy, weak=False)
            user_service.add_role_to_user(user, role)
            spy.assert_called_with(user, role=role)

    def test_can_remove_role_from_user(self):
        """ Removing role from user """
        with events.events.disconnect_receivers():
            user = self.create_user()
            role = Role(handle='test_role', title='Testing')
            ok = role_service.save(role)
            if not ok:
                self.fail('Role invalid')

            user_service.add_role_to_user(user, role)
            self.assertTrue(user.has_role(role))

            user_service.remove_role_from_user(user, role)
            self.assertFalse(user.has_role(role))

    def test_removing_role_emits_event(self):
        """ Removing role form a user emits event """
        with user_events.disconnect_receivers():
            user = self.create_user()
            role = Role(handle='test_role', title='Testing')
            role_service.save(role, user)
            user_service.add_role_to_user(user, role)

            spy = mock.Mock()
            events.user_lost_role_event.connect(spy, weak=False)
            user_service.remove_role_from_user(user, role)
            spy.assert_called_with(user, role=role)

    # -------------------------------------------------------------------------
    # JWT tokens
    # -------------------------------------------------------------------------

    def test_user_service_receives_jwt_options(self):
        """ Initializing user service with config options """
        class CustomConfig(DefaultConfig):
            USER_JWT_SECRET='SuperSecret'
            USER_JWT_ALGO='FAKE526'
            USER_JWT_LIFETIME_SECONDS=-1
            USER_JWT_IMPLEMENTATION=None
            USER_JWT_LOADER_IMPLEMENTATION=None

        cfg = CustomConfig()
        app = bootstrap.create_app('demo', config=cfg)
        bootstrap.add_users(app)

        self.assertEquals(
            cfg.get('USER_JWT_SECRET'),
            user_service.jwt_secret
        )
        self.assertEquals(
            cfg.get('USER_JWT_ALGO'),
            user_service.jwt_algo
        )
        self.assertEquals(
            cfg.get('USER_JWT_LIFETIME_SECONDS'),
            user_service.jwt_lifetime
        )
        self.assertEquals(
            cfg.get('USER_JWT_IMPLEMENTATION'),
            user_service.jwt_implementation
        )
        self.assertEquals(
            cfg.get('USER_JWT_LOADER_IMPLEMENTATION'),
            user_service.jwt_loader_implementation
        )

    def test_default_token_implementation(self):
        """ Generating token using default implementation"""
        user = self.create_user(confirm_email=True)
        token = user_service.default_token_implementation(user.id)
        self.assertEquals(str, type(token))
        decoded = jwt.decode(
            token,
            user_service.jwt_secret,
            algorithms=[user_service.jwt_algo]
        )
        self.assertEquals(user.id, decoded['user_id'])

    def test_default_implementation_fails_if_user_not_found(self):
        """ Fail to generate token if user not found """
        with self.assertRaises(x.JwtNoUser):
            user_service.get_token(111)

    def test_default_implemnetation_returns_token_on_file_if_got_one(self):
        """ Return token from user model if it's still valid"""
        with user_events.disconnect_receivers():
            user = self.create_user(confirm_email=True)
        from_now = timedelta(seconds=user_service.jwt_lifetime)
        expires = datetime.utcnow() + from_now
        data = dict(exp=expires, user_id=user.id)
        token = jwt.encode(
            data,
            user_service.jwt_secret,
            algorithm=user_service.jwt_algo
        )
        user._token = token
        user_service.save(user)
        token = user_service.get_token(user.id)
        self.assertEquals(user._token, token)

    def test_default_implementation_regenerates_token_if_expired(self):
        """ Regenerate user token if the one on file expired"""
        with user_events.disconnect_receivers():
            user = self.create_user(confirm_email=True)
        from_now = timedelta(seconds=-20)
        expires = datetime.utcnow() + from_now
        data = dict(exp=expires, user_id=user.id)
        token = jwt.encode(
            data,
            user_service.jwt_secret,
            algorithm=user_service.jwt_algo
        )
        user._token = token
        user_service.save(user)
        token = user_service.get_token(user.id)
        self.assertEquals(token, user._token)

    def test_default_tokens_fail_if_tampered_with(self):
        """ Default tokens fail if tampered with"""
        with user_events.disconnect_receivers():
            user = self.create_user(confirm_email=True)
        token = user_service.default_token_implementation(user.id)
        with self.assertRaises(jwt.exceptions.DecodeError):
            jwt.decode(
                token + 'x',
                user_service.jwt_secret,
                algorithms=[user_service.jwt_algo]
            )

    def test_default_tokens_fail_if_expired(self):
        """ Default tokens will fail to decode upon expiration"""
        with user_events.disconnect_receivers():
            user = self.create_user(confirm_email=True)
        user_service.jwt_lifetime = -1
        token = user_service.default_token_implementation(user.id)
        with self.assertRaises(jwt.exceptions.ExpiredSignatureError):
            jwt.decode(
                token,
                user_service.jwt_secret,
                algorithms=[user_service.jwt_algo]
            )

        # cleanup
        user_service.jwt_lifetime = 86400

    def test_default_token_user_loader_fails_if_tampered_with(self):
        """ Default token user loader fails if tampered with """
        with user_events.disconnect_receivers():
            user = self.create_user()
            token = user_service.default_token_implementation(user.id)
            token = 'xxx' + token
            with self.assertRaises(x.JwtDecodeError):
                user_service.default_token_user_loader(token)

    def test_default_token_user_loader_fails_if_expired(self):
        """ Default token user loader fails if expired """
        with user_events.disconnect_receivers():
            user = self.create_user()
            user_service.jwt_lifetime = -1
            token = user_service.default_token_implementation(user.id)
            with self.assertRaises(x.JwtExpired):
                user_service.default_token_user_loader(token)

    def test_default_token_user_loader_fails_if_no_user(self):
        """ Default token user loader fails if user not found """
        with user_events.disconnect_receivers():
            user_service.jwt_lifetime = 86400
            user = self.create_user(confirm_email=True)
            token = user_service.default_token_implementation(user.id)
            user_service.delete(user)
            with self.assertRaises(x.JwtNoUser):
                user_service.default_token_user_loader(token)

    def test_default_token_user_loader_fails_if_account_locked(self):
        """ Default token user loader fails if account locked """
        with user_events.disconnect_receivers():
            user = self.create_user()
            user.lock_account(minutes=1)
            user_service.save(user)
            token = user_service.default_token_implementation(user.id)
            with self.assertRaises(x.AccountLocked):
                user_service.default_token_user_loader(token)

    def test_default_token_loader_fails_if_email_not_confirmed(self):
        """ Default token user loader fails if email unconfirmed"""
        with user_events.disconnect_receivers():
            user = self.create_user(confirm_email=False)
        token = user_service.default_token_implementation(user.id)
        with self.assertRaises(x.EmailNotConfirmed):
            user_service.default_token_user_loader(token)

    def test_default_token_loader_fails_if_tokens_mismatch(self):
        """ Fail to load user if token doesn't match the one on file"""
        with user_events.disconnect_receivers():
            user = self.create_user()
        token = user_service.default_token_implementation(user.id)
        user_service.revoke_user_token(user.id)
        with self.assertRaises(x.JwtTokenMismatch):
            user_service.default_token_user_loader(token)

    def test_default_token_user_loader_can_load_user(self):
        """ Load user by token using default loader"""
        with user_events.disconnect_receivers():
            user = self.create_user()
            token = user_service.default_token_implementation(user.id)
            loaded = user_service.default_token_user_loader(token)
            self.assertEquals(loaded, user)

    def test_fall_back_to_default_token_implementation_if_no_custom(self):
        """ Fall back to default token implementation if no custom """
        with user_events.disconnect_receivers():
            user = self.create_user()

        token = user_service.get_token(user.id)
        decoded = user_service.decode_token(token)
        self.assertEquals(user.id, decoded['user_id'])
        for claim in ['exp', 'nbf', 'iat', 'user_id']:
            self.assertTrue(claim in decoded.keys())
        self.assertEquals(4, len(decoded.keys()))

    def test_fall_back_to_default_token_loader_if_no_custom(self):
        """ Fall back to default token user loader if no custom"""
        user_service.jwt_loader_implementation = None
        with user_events.disconnect_receivers():
            user = self.create_user()
            token = user_service.get_token(user.id)
            loaded = user_service.get_user_by_token(token)
            self.assertEquals(loaded, user)

    def test_raise_when_failing_to_import_custom_token_implementation(self):
        """ Raising exception if custom token implementation fails to import"""
        class CustomConfig(DefaultConfig):
            USER_JWT_SECRET='SuperSecret'
            USER_JWT_IMPLEMENTATION='nonexistent.nonexistent'

        cfg = CustomConfig()
        app = bootstrap.create_app('demo', config=cfg)
        bootstrap.add_users(app)
        with self.assertRaises(x.ConfigurationException):
            user_service.get_token(123)

    def test_can_use_custom_token_implementation(self):
        """ Can register and use custom token implementation"""
        token = 'tests.user_tests.user_service_test.custom_token_implementation'

        class CustomConfig(DefaultConfig):
            USER_JWT_SECRET = 'SuperSecret'
            USER_JWT_LIFETIME_SECONDS=10
            USER_JWT_IMPLEMENTATION=token

        cfg = CustomConfig()
        app = bootstrap.create_app('demo', config=cfg)
        bootstrap.add_users(app)
        user_id = 123
        token = user_service.get_token(user_id)
        expected = custom_token_implementation(user_id)
        self.assertEquals(expected, token)

    def test_raise_when_failing_to_import_custom_token_loader(self):
        """ Raising exception if custom token loader fails to import"""
        class CustomConfig(DefaultConfig):
            USER_JWT_SECRET='SuperSecret'
            USER_JWT_LOADER_IMPLEMENTATION='nonexistent.nonexistent'

        cfg = CustomConfig()
        app = bootstrap.create_app('demo', config=cfg)
        bootstrap.add_users(app)
        with self.assertRaises(x.ConfigurationException):
            user_service.get_user_by_token(123)

    def test_can_use_custom_token_loader(self):
        """ Can register and use custom token user loader"""
        loader = 'tests.user_tests.user_service_test.custom_token_loader'

        class CustomConfig(DefaultConfig):
            USER_JWT_SECRET='SuperSecret'
            USER_JWT_IMPLEMENTATION=None
            USER_JWT_LOADER_IMPLEMENTATION=loader

        cfg = CustomConfig()
        app = bootstrap.create_app('demo', config=cfg)
        bootstrap.add_users(app)
        loaded = user_service.get_user_by_token(123)
        expected = custom_token_loader(123)
        self.assertEquals(expected, loaded)























