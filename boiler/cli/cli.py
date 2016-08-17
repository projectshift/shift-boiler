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
def run(host='0.0.0.0', port=5000, reload=True, debug=True):
    """ Run development server """
    from werkzeug.serving import run_simple
    from boiler.bootstrap import create_middleware
    from config.config import DevConfig

    app = create_middleware(config=DevConfig())
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
    context = dict()

    # mount apps
    from boiler.bootstrap import create_middleware
    middleware = create_middleware()
    context['apps'] = dict(frontend=middleware.app)
    for mount in middleware.mounts:
        context['apps'][mount] = middleware.mounts[mount]

    # and push app context
    app_context = middleware.app.app_context()
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

# @todo: how can we intercept these args
nose_argv = None
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    nose_argv = sys.argv[2:]
    sys.argv = sys.argv[:2]


@cli.command(name='test')
def test():
    """ Run application tests """
    from nose import run
    params = ['__main__', '-c', 'nose.ini']
    params.extend(nose_argv)
    run(argv=params)





