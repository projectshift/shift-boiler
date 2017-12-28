from unittest import mock
from nose.plugins.attrib import attr
from boiler.tests.base_testcase import BoilerTestCase

from boiler import bootstrap
from boiler.config.default_config import DefaultConfig



@attr('feature', 'user')
class UserFeatureTests(BoilerTestCase):

    # ------------------------------------------------------------------------
    # General
    # ------------------------------------------------------------------------

    @attr('zzz')
    def test_fail_to_init_feature_if_jwt_secret_not_set(self):
        """ Fail to initialize users feature without JWT secret"""
        config = DefaultConfig()
        print('SECRET SHOULD BE NONE', config.get('USER_JWT_SECRET'))
        app = bootstrap.create_app('demo', config=config)
        print('SECRET SHOULD BE NONE', app.config.get('USER_JWT_SECRET'))
        # bootstrap.add_users(app)


    def test_user_service_receives_config_options(self):
        """ Initializing user service with config options """
        pass

    def test_user_model_receives_config_options(self):
        """ User model is initialised with JWT config options"""
        pass








