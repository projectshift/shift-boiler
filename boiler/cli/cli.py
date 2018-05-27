import click, os, sys, shutil
from boiler.cli.colors import *


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
@click.option(
    '--environment',
    '-e',
    default='development',
    help='Environment to use'
)
def run(host='0.0.0.0', port=5000, reload=True, debug=True, environment='dev'):
    """ Run development server """
    from werkzeug.serving import run_simple
    from boiler.bootstrap import init
    from config.config import DevConfig, TestingConfig, DefaultConfig
    from config.app import app as app_init

    # get config
    if environment == 'production':
        app_init['config'] = DefaultConfig()
    elif environment == 'testing':
        app_init['config'] = TestingConfig()
    else:
        app_init['config'] = DevConfig()

    app = init(app_init['module'], app_init['config'])
    return run_simple(
        hostname=host,
        port=port,
        application=app,
        use_reloader=reload,
        use_debugger=debug,
    )


@cli.command(name='shell')
@click.option(
    '--environment',
    '-e',
    default='development',
    help='Environment to use'
)
def shell(environment='dev'):
    """ Start application-aware shell """
    from boiler.bootstrap import init
    from config.app import app as app_init
    from config.config import DevConfig, TestingConfig, DefaultConfig

    # get config
    if environment == 'production':
        app_init['config'] = DefaultConfig()
    elif environment == 'testing':
        app_init['config'] = TestingConfig()
    else:
        app_init['config'] = DevConfig()

    # create app
    app = init(app_init['module'], app_init['config'])
    context = dict(app=app)

    # and push app context
    app_context = app.app_context()
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




