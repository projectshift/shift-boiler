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
    default = current_app.config.get('PASSLIB_ALGO')
    schemes = current_app.config.get('PASSLIB_SCHEMES')
except RuntimeError as e:
    raise RuntimeError('Unable to get config: ' + str(e))

passlib_context = CryptContext(
    schemes=schemes,
    default=default,
)
