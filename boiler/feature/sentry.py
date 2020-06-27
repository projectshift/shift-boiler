import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


def sentry_feature(app):
    """
    Sentry feature
    Adds basic integration with Sentry via the raven library
    """

    # get keys
    sentry_key = app.config.get('SENTRY_KEY')
    sentry_project_id = app.config.get('SENTRY_PROJECT_ID')
    sentry_ingest_url = app.config.get('SENTRY_INGEST_URL')
    if not sentry_key or not sentry_project_id or not sentry_ingest_url:
        return

    # prepare dsn
    dsn = 'https://{key}@{ingest_url}/{project_id}'.format(
        key=sentry_key,
        ingest_url=sentry_ingest_url,
        project_id=sentry_project_id
    )

    # init sentry
    sentry_sdk.init(
        dsn=dsn,
        integrations=[FlaskIntegration()]
    )