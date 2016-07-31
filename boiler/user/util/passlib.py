from passlib.context import CryptContext
from flask import current_app

"""
Note on bcrypt
Hashing passwords with bcrypt algorithm will require a python bcrypt module.
On Mac OSX this may sometime fail due to the absence of libffi. If that is
the case, you can install it with homebrew:

    brew install pkg-config libffi
    pip install bcrypt

@see https://stackoverflow.com/questions/22875270/error-installing-bcrypt-with-pip-on-os-x-cant-find-ffi-h-libffi-is-installed/25854749#25854749
"""

# get app config (bootstrapped application required)
try:
    config = current_app.config
    config = config['PASSLIB']

    default = config['default']
    schemes = list(config['schemes'].keys())
    default_rounds = {}
    for scheme in config['schemes']:
        key = scheme + '__default_rounds'
        default_rounds[key] = config['schemes'][scheme]

except RuntimeError as e:
    raise RuntimeError('Unable to get config: ' + str(e))

passlib_context = CryptContext(

    # schemes
    schemes=schemes,
    default=default,

    # vary rounds parameter randomly
    all__vary_rounds=0.1,

    # default schemes costs
    **default_rounds
)
