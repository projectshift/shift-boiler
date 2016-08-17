from unittest import mock
from nose.plugins.attrib import attr
from boiler.testing.testcase import BaseTestCase

from datetime import datetime, timedelta
from flask import session
from shiftschema.result import Result

from boiler.feature.mail import mail
from boiler.user.services import user_service, role_service
from boiler.user import events, exceptions as x
from boiler.user.events import events as user_events
from boiler.user.models import User, Role
from boiler.user.user_service import UserService


@attr('user', 'service')
class UserServiceTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.create_db()

    def create_user(self, confirm_email=True):
        """ A shortcut to quickly create and return a user """
        with user_events.disconnect_receivers():
            user = user_service.create(
                username='tester',
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

    def test_save(self):
        """ Persisting user """
        user = User(email='test@test.com', username='tester', password='123')
        with user_events.disconnect_receivers():
            user_service.save(user)
        self.assertEqual(1, user.id)

    def test_save_emits_event(self):
        """ Saving a user emits event """
        user = User(email='test@test.com', username='tester', password='123')
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
            result = user_service.register(
                username='tester',
                email='not.email',
                password='123'
            )
            self.assertIsInstance(result, Result)
            self.assertFalse(result)

    def test_register(self):
        """ Can register new user """
        with user_events.disconnect_receivers():
            user = user_service.register(
                username='tester',
                email='test@test.com',
                password='123'
            )
            self.assertIsInstance(user, User)
            self.assertEqual(1, user.id)

    def test_register_password_can_be_verified(self):
        """ REGRESSION: Password provided at registration can be verified """
        data = dict(
            username = 'tester',
            email = 'tester@test.com',
            password = '111111',
        )

        with user_events.disconnect_receivers():
            user = user_service.register(**data)

        verified = user.verify_password(data['password'])
        self.assertTrue(verified)

        password = 222222
        user.password = password
        user_service.save(user)
        verified = user.verify_password(password)
        self.assertTrue(verified)

    def test_register_emits_event(self):
        """ Registration emits event """
        event = events.register_event
        with user_events.disconnect_receivers():
            spy = mock.Mock()
            event.connect(spy, weak=False)
            user = user_service.register(
                username='tester',
                email='test@test.com',
                password='123'
            )
            spy.assert_called_with(user)

    def test_welcome_message_send(self):
        """ Welcome message can be sent """
        user = User(email='test@test.com', username='tester', password='123')
        with mail.record_messages() as out:
            with self.app.test_request_context():
                url = 'http://my.confirm.url/'
                user_service.send_welcome_message(user, url)

            msg = out[0]
            self.assertTrue('Confirm email' in msg.html)
            self.assertTrue('Confirm email' in msg.body)
            self.assertTrue(user.email_link in msg.html)
            self.assertTrue(user.email_link in msg.body)

    def test_welcome_message_resend(self):
        """ Welcome message can be resent """
        with events.events.disconnect_receivers():
            with self.app.test_request_context():
                u = user_service.register(
                    username='test',
                    email='tester@test.com',
                    password='123456'
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
    # Change email an confirmation
    # -------------------------------------------------------------------------

    def test_change_email_returns_validation_errors(self):
        """ Change email returns validation errors on bad data """
        u = User(email='ok@ok.com', username='user', password='123')
        with events.events.disconnect_receivers():
            res = user_service.change_email(u, 'not-an-email')
            self.assertIsInstance(res, Result)

    def test_change_email_possible(self):
        """ Email change procedure is possible"""
        with events.events.disconnect_receivers():
            with self.app.test_request_context():
                u = self.create_user()
                user_service.force_login(u)
                self.assertTrue('user_id' in session)

                res = user_service.change_email(u, 'new@email.com')
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
                user_service.change_email(u, 'new@email.com')
                spy.assert_called_with(u)

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
        u.username = '1'  # trigger error
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























