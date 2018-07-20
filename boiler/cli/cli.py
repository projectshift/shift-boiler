import click, os
from werkzeug.utils import import_string
from boiler.cli.colors import *
from boiler import exceptions as x
from boiler.bootstrap import load_dotenvs

load_dotenvs()

# -----------------------------------------------------------------------------
# Group setup
# -----------------------------------------------------------------------------


@click.group(help=yellow('Welcome to project console!'))
def cli():
    pass


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------

def get_config():
    """
    Imports config based on environment.
    :return:
    """
    app_module = os.getenv('APP_MODULE')
    if not app_module:
        err = 'Unable to bootstrap application APP_MODULE is not defined'
        raise x.BootstrapException(err)

    app_config = os.getenv('APP_CONFIG')
    if not app_module:
        err = 'Unable to bootstrap application APP_CONFIG is not defined'
        raise x.BootstrapException(err)

    try:
        config_class = import_string(app_config)
    except ImportError:
        err = 'Failed imported config file [{}]'
        raise x.BootstrapException(err.format(app_config))

    # and return
    config = config_class()
    return config


@cli.command(name='run')
@click.option('--host', '-h', default='0.0.0.0', help='Bind to')
@click.option('--port', '-p', default=5000, help='Listen on port')
@click.option('--reload/--no-reload', default=True, help='Reload on change?')
@click.option('--debug/--no-debug', default=True, help='Use debugger?')
def run(host='0.0.0.0', port=5000, reload=True, debug=True):
    """ Run development server """
    from werkzeug.serving import run_simple
    from boiler.bootstrap import init

    # create app
    app_module = os.getenv('APP_MODULE')
    config = get_config()
    app = init(app_module, config)

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
    from boiler.bootstrap import init

    # create app
    app_module = os.getenv('APP_MODULE')
    config = get_config()
    app = init(app_module, config)
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




