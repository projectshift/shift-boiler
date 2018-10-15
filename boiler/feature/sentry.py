from raven.contrib.flask import Sentry

sentry = Sentry()


def sentry_feature(app):
    """
    Sentry feature
    Adds basic integration with Sentry via the raven library
    """

    # get keys
    sentry_public_key = app.config.get('SENTRY_PUBLIC_KEY')
    sentry_project_id = app.config.get('SENTRY_PROJECT_ID')
    if not sentry_public_key or not sentry_project_id:
        return

    # prepare dsn
    dsn = 'https://{key}@sentry.io/{project_id}'
    dsn = dsn.format(key=sentry_public_key, project_id=sentry_project_id)

    # init sentry
    sentry.init_app(app=app, dsn=dsn)