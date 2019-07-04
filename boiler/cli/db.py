import click
from alembic import command as alembic_command
from alembic.util import CommandError
from boiler.cli.colors import *

from boiler.feature.orm import db
from boiler import bootstrap


def get_config():
    """
    Prepare and return alembic config
    These configurations used to live in alembic config initialiser, but that
    just tight coupling. Ideally we should move that to userspace and find a
    way to pass these into alembic commands.

    @todo: think about it
    """
    from boiler.migrations.config import MigrationsConfig

    # used for errors
    map = dict(
        path='MIGRATIONS_PATH',
        db_url='SQLALCHEMY_DATABASE_URI',
        metadata='SQLAlchemy metadata'
    )

    app = bootstrap.get_app()
    params = dict()
    params['path'] = app.config.get(map['path'], 'migrations')
    params['db_url'] = app.config.get(map['db_url'])
    params['metadata'] = db.metadata

    for param, value in params.items():
        if not value:
            msg = 'Configuration error: [{}] is undefined'
            raise Exception(msg.format(map[param]))

    config = MigrationsConfig(**params)
    return config


# -----------------------------------------------------------------------------
# Group setup
# -----------------------------------------------------------------------------


@click.group(help=yellow('Database management commands'))
def cli():
    pass


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------


@cli.command(name='init')
def init():
    """ Initialize new migrations directory """
    try:
        config = get_config()
        alembic_command.init(config, config.dir, 'project')
    except CommandError as e:
        click.echo(red(str(e)))


@cli.command(name='revision')
@click.option('--revision', type=str, default=None, help='Specify a hardcoded revision id instead of generating one')
@click.option('--path', type=str, default=None, help='Specify a hardcoded revision id instead of generating one')
@click.option('--branch-label', type=str, default=None, help='Specify a branch label to apply to the new revision')
@click.option('--splice', type=bool, is_flag=True, default=False, help='Allow a non-head revision as the "head" to splice onto')
@click.option('--head', type=str, default=None, help='Specify head revision or <branch>@head to base new revision on')
@click.option('--sql', type=bool, is_flag=True, default=False, help='Do not execute SQL - dump to standard output instead')
@click.option('--autogenerate', type=bool, is_flag=True, default=False, help='Populate revision with autoganerated diff')
@click.option('--message', '-m', type=str, default=None, help='Migration title')
def revision(revision, path, branch_label, splice, head, sql, autogenerate, message):
    """ Create new revision file """
    alembic_command.revision(
        config=get_config(),
        rev_id=revision,
        version_path=path,
        branch_label=branch_label,
        splice=splice,
        head=head,
        sql=sql,
        autogenerate=autogenerate,
        message=message
    )


@cli.command('generate')
@click.option('--revision', type=str, default=None, help='Specify a hardcoded revision id instead of generating one')
@click.option('--path', type=str, default=None, help='Specify a hardcoded revision id instead of generating one')
@click.option('--branch-label', type=str, default=None, help='Specify a branch label to apply to the new revision')
@click.option('--splice', type=bool, is_flag=True, default=False, help='Allow a non-head revision as the "head" to splice onto')
@click.option('--head', type=str, default=None, help='Specify head revision or <branch>@head to base new revision on')
@click.option('--sql', type=bool, is_flag=True, default=False, help='Do not execute SQL - dump to standard output instead')
@click.option('--message', '-m', type=str, default=None, help='Migration title')
def generate(revision, path, branch_label, splice, head, sql, message):
    """ Autogenerate new revision file """
    alembic_command.revision(
        config=get_config(),
        rev_id=revision,
        version_path=path,
        branch_label=branch_label,
        splice=splice,
        head=head,
        sql=sql,
        autogenerate=True,
        message=message
    )


@cli.command(name='merge')
@click.option('--revision', type=str, default=None, help='Specify a hardcoded revision id instead of generating one')
@click.option('--branch-label', type=str, default=None, help='Specify a branch label to apply to the new revision')
@click.option('--message', '-m', type=str, default=None, help='Migration title')
@click.option('--list-revisions', type=str, default=None, help='One or more revisions, or "heads" for all heads')
def merge(revision, branch_label, message, list_revisions=''):
    """ Merge two revision together, create new revision file """
    alembic_command.merge(
        config=get_config(),
        revisions=list_revisions,
        message=message,
        branch_label=branch_label,
        rev_id=revision
    )


@cli.command(name='up')
@click.option('--tag', type=str, default=None, help='Arbitrary tag name (used by custom env.py)')
@click.option('--sql', type=bool, is_flag=True, default=False, help='Do not execute SQL - dump to standard output instead')
@click.option('--revision', type=str, default='head', help='Revision id')
def up(tag, sql, revision):
    """ Upgrade to revision """
    alembic_command.upgrade(
        config=get_config(),
        revision=revision,
        sql=sql,
        tag=tag
    )


@cli.command(name='down')
@click.option('--tag', type=str, default=None, help='Arbitrary tag name (used by custom env.py)')
@click.option('--sql', type=bool, is_flag=True, default=False, help='Do not execute SQL - dump to standard output instead')
@click.option('--revision', type=str, default='-1', help='Revision id')
def down(tag, sql, revision):
    """ Downgrade to revision """
    alembic_command.downgrade(
        config=get_config(),
        revision=revision,
        sql=sql,
        tag=tag
    )


@cli.command(name='show')
@click.option('--revision', type=str, default='head', help='Revision id')
def show(revision):
    """ Show the revisions """
    alembic_command.show(
        config=get_config(),
        rev=revision
    )


@cli.command(name='history')
@click.option('--verbose', '-v', type=bool, is_flag=True, default=False, help='Use more verbose output')
@click.option('--range', '-r', type=str, default=None, help='Specify a revision range; format is [start]:[end]')
def history(verbose, range):
    """ List revision changesets chronologically """
    alembic_command.history(
        config=get_config(),
        rev_range=range,
        verbose=verbose
    )


@cli.command(name='heads')
@click.option('--resolve', '-r', type=bool, is_flag=True, default=False, help='Treat dependency versions as down revisions')
@click.option('--verbose', '-v', type=bool, is_flag=True, default=False, help='Use more verbose output')
def heads(resolve, verbose):
    """ Show available heads """
    alembic_command.heads(
        config=get_config(),
        verbose=verbose,
        resolve_dependencies=resolve
    )


@cli.command(name='branches')
@click.option('--verbose', '-v', type=bool, is_flag=True, default=False, help='Use more verbose output')
def branches(verbose):
    """ Show current branch points """
    alembic_command.branches(
        config=get_config(),
        verbose=verbose
    )


@cli.command(name='current')
@click.option('--verbose', '-v', type=bool, is_flag=True, default=False, help='Use more verbose output')
def current(verbose):
    """ Display current revision """
    alembic_command.current(
        config=get_config(),
        verbose=verbose
    )


@cli.command()
@click.option('--tag', type=str, default=None, help='Arbitrary tag name (used by custom env.py)')
@click.option('--sql', type=bool, is_flag=True, default=False, help='Do not execute SQL - dump to standard output instead')
@click.option('--revision', type=str, default='head', help='Revision id')
def stamp(revision, sql, tag):
    """ Stamp db to given revision without migrating """
    alembic_command.stamp(
        config=get_config(),
        revision=revision,
        sql=sql,
        tag=tag
    )

