import click, os, sys, shutil
from boiler.cli.colors import *
from click import echo


# -----------------------------------------------------------------------------
# Group setup
# -----------------------------------------------------------------------------


@click.group(help=yellow('Welcome to project console!'))
def cli():
    pass


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------

@cli.command(name='run')
@click.option('--host', '-h', default='0.0.0.0', help='Bind to')
@click.option('--port', '-p', default=5000, help='Listen on port')
@click.option('--reload/--no-reload', default=True, help='Reload on change?')
@click.option('--debug/--no-debug', default=True, help='Use debugger?')
@click.option('--environment', '-e', default='dev', help='Environment to use)')
def run(host='0.0.0.0', port=5000, reload=True, debug=True, environment='dev'):
    """ Run development server """
    from werkzeug.serving import run_simple
    from boiler.bootstrap import create_middleware
    from config.config import DevConfig, TestingConfig, DefaultConfig
    from config.apps import apps

    # get config
    if environment == 'prod': config = DefaultConfig()
    elif environment == 'test': config = TestingConfig()
    else: config = DevConfig()

    # use dev config for every app when run this way
    for app_name in apps['apps'].keys():
        apps['apps'][app_name]['config'] = config

    app = create_middleware(apps=apps)
    return run_simple(
        hostname=host,
        port=port,
        application=app,
        use_reloader=reload,
        use_debugger=debug,
    )


@cli.command(name='shell')
def shell():
    """ Start application-aware shell """
    from boiler.bootstrap import create_middleware
    from config.config import DevConfig
    from config.apps import apps

    # use dev config for every app when run this way
    for app_name in apps['apps'].keys():
        apps['apps'][app_name]['config'] = DevConfig()

    # mount apps
    context = dict()
    middleware = create_middleware(apps=apps)
    context['middleware'] = middleware.wsgi_app
    default = apps['default_app']
    context['apps'] = dict()
    context['apps'][default] = middleware.wsgi_app.app

    # for app in middleware.wsgi_app.mounts:
    for mount, app in middleware.wsgi_app.mounts.items():
        for name, cfg in apps['apps'].items():
            if mount == cfg['base_url']:
                context['apps'][name] = app

    # and push app context
    app_context = middleware.app_context()
    app_context.push()

    # and run
    try:
        from IPython import embed
        embed(user_ns=context)
    except ImportError:
        import code
        code.interact(local=context)


# -----------------------------------------------------------------------------
# Testing commands
# -----------------------------------------------------------------------------

@cli.command(name='test',context_settings=dict(ignore_unknown_options=True))
@click.argument('nose_argsuments', nargs=-1, type=click.UNPROCESSED)
def test(nose_argsuments):
    """ Run application tests """
    from nose import run
    params = ['__main__', '-c', 'nose.ini']
    params.extend(nose_argsuments)
    run(argv=params)




