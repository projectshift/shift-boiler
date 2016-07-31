from werkzeug.urls import url_encode
from flask import current_app, json, render_template, request
from wtforms.fields import Field
from wtforms import ValidationError
from speaklater import _LazyString
from urllib import request as http

"""
Recaptcha
This set of classes allow you to use skinnable custom recaptcha fields
in your WTF form objects. Its a slight rewrite of the original recaptcha
field from Flask-WTF package that only supports Recaptcha v2, wich is not
always what we want. Sometimes we just want a regular image captcha.
"""

class _JSONEncoder(json.JSONEncoder):
    """ Lazy string encoder """
    def default(self, o):
        if isinstance(o, _LazyString): return str(o)
        return json.JSONEncoder.default(self, o)


class RecaptchaWidget():
    """ Recaptcha renderer """

    def translations(self, gettext=None):
        """
        Connect translations to gettext
        This is entirely optional and will just fall back to untranslated
        strings
        """
        if not gettext:
            gettext = lambda x: x

        translations = dict(
            audio_challenge = gettext('Get an audio challenge'),
            cant_hear_this = gettext('Download sound as MP3'),
            help_btn = gettext('Help'),
            image_alt_text = gettext('reCAPTCHA challenge image'),
            incorrect_try_again = gettext('Incorrect. Try again.'),
            instructions_audio = gettext('Type what you hear'),
            instructions_visual = gettext('Type the text'),
            play_again = gettext('Play sound again'),
            privacy_and_terms = gettext('Privacy & Terms'),
            refresh_btn = gettext('Get a new challenge'),
            visual_challenge = gettext('Get a visual challenge')
        )

        for item in translations.keys():
            translations[item] = gettext(translations[item])

        return translations

    def __call__(self, field, template='recaptcha/base.j2', **kwargs):
        """Returns the recaptcha input HTML."""

        options = dict(
            theme='clean',
            custom_translations=self.translations(field.gettext)
        )

        options.update(current_app.config.get('RECAPTCHA_OPTIONS', {}))
        server = '//www.google.com/recaptcha/api/'
        server = current_app.config.get('RECAPTCHA_API_SERVER', server)
        query = url_encode(dict(
            k=current_app.config['RECAPTCHA_PUBLIC_KEY'],
            error=field.recaptcha_error)
        )

        params = dict(
            script_url='{}challenge?{}'.format(server, query),
            frame_url='{}noscript?{}'.format(server, query),
            options=json.dumps(options, cls=_JSONEncoder)
        )

        return render_template(template, **params)


class RecaptchaValidator():
    """ Validates recaptcha """

    @property
    def errors(self):
        errors = dict()
        errors['invalid-site-public-key'] = 'Public key is invalid'
        errors['invalid-site-private-key'] = 'Private key is invalid'
        errors['invalid-referrer'] = 'Invalid public key domain'
        errors['verify-params-incorrect'] = 'Incorrect recaptcha parameters'
        return errors

    def __init__(self, message='Invalid solution. Please try again.'):
        self.message = message

    def __call__(self, form, field):
        if current_app.testing:
            return True

        if request.json:
            challenge = request.json.get('recaptcha_challenge_field', '')
            response = request.json.get('recaptcha_response_field', '')
        else:
            challenge = request.form.get('recaptcha_challenge_field', '')
            response = request.form.get('recaptcha_response_field', '')

        if not challenge or not response:
            raise ValidationError(field.gettext(self.message))

        remote_ip = request.remote_addr

        if not self._validate(challenge, response, remote_ip):
            field.recaptcha_error = 'incorrect-captcha-sol'
            raise ValidationError(field.gettext(self.message))

    def _validate(self, challenge, response, remote_addr):
        """ Performs the actual validation"""
        private_key = current_app.config['RECAPTCHA_PRIVATE_KEY']

        data = url_encode(dict(
            privatekey=private_key,
            remoteip=remote_addr,
            challenge=challenge,
            response=response
        ))

        server = 'https://www.google.com/recaptcha/api/verify'
        response = http.urlopen(server, bytes(data, encoding='utf8'))

        if response.code != 200:
            return False

        rv = [l.decode('utf8').strip() for l in response.readlines()]
        for l in rv: print(l)

        if rv and rv[0] == 'true':
            return True

        if len(rv) > 1:
            error = rv[1]
            if error in self.errors:
                raise RuntimeError(self.errors[error])

        return False

class RecaptchaField(Field):
    """ Recatch field to be used in your forms """
    widget = RecaptchaWidget()
    recaptcha_error = None

    def __init__(self, label='', **kwargs):
        validators = [RecaptchaValidator()]
        super(RecaptchaField, self).__init__(label, validators, **kwargs)