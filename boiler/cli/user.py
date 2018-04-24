import click
from boiler.cli.colors import *
from boiler.user.models import User, Role
from boiler.user.services import user_service, role_service
from boiler.cli import get_app

def print_validation_errors(result):
    """ Accepts validation result object and prints report (in red)"""
    click.echo(red('\nValidation failed:'))
    click.echo(red('-' * 40))
    messages = result.get_messages()
    for property in messages.keys():
        click.echo(yellow(property + ':'))
        for error in messages[property]:
            click.echo(red('* ' + error))
        click.echo('')


def find_user(search_params):
    """
    Find user
    Attempts to find a user by a set of search params. You must be in
    application context.
    """
    user = None
    params = {prop: value for prop, value in search_params.items() if value}
    if 'id' in params or 'email' in params:
        user = user_service.first(**params)
    return user

# -----------------------------------------------------------------------------
# Group setup
# -----------------------------------------------------------------------------


@click.group(help=yellow('User management commands'))
def cli():
    pass


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------

@cli.command(name='create-user')
@click.option('--email', type=str, default=None, prompt=True)
@click.option('--password', type=str, hide_input=True, prompt=True, confirmation_prompt=True)
def create(email, password):
    """ Creates a new user record """
    with get_app().app_context():
        user = User(email=email, password=password)
        result = user_service.save(user)
        if not isinstance(result, User):
            print_validation_errors(result)
            return

        click.echo(green('\nUser created:'))
        click.echo(green('-' * 40))
        click.echo(str(user) + '\n')


@cli.command(name='find-user')
@click.option('--id', type=int, default=None)
@click.option('--email', type=str, default=None)
def find(*_, **kwargs):
    """ Find user by id/email"""
    click.echo(green('\nFind user:'))
    click.echo(green('-' * 40))

    with get_app().app_context():
        user = find_user(kwargs)

    if not user:
        click.echo(red('Not found\n'))
        return

    click.echo(str(user) + '\n')
    return


@cli.command(name='change-password')
@click.option('--user_id', type=int, default=None, prompt=True)
@click.option('--password', type=str, hide_input=True, prompt=True, confirmation_prompt=True)
def change_password(*_, user_id=None, password=None):
    """ Change user password """
    click.echo(green('\nChange password:'))
    click.echo(green('-' * 40))

    with get_app().app_context():
        user = find_user(dict(id=user_id))
        if not user:
            click.echo(red('User not found\n'))
            return

        result = user_service.change_password(user, password)
        if isinstance(result, User):
            msg = 'Changed password for user {} \n'.format(user.email)
            click.echo(green(msg))
            return

        print_validation_errors(result)
        return


@cli.command(name='change-email')
@click.option('--user_id', type=int, default=None, prompt=True)
@click.option('--new_email', type=str, prompt=True, confirmation_prompt=True)
def change_email(*_, user_id=None, new_email=None):
    """ Change email for a user """
    click.echo(green('\nChange email:'))
    click.echo(green('-' * 40))

    with get_app().app_context():
        user = find_user(dict(id=user_id))
        if not user:
            click.echo(red('User not found\n'))
            return

        user.email = new_email
        result = user_service.save(user)
        if not isinstance(result, User):
            print_validation_errors(result)
            return

        user.confirm_email()
        user_service.save(user)
        msg = 'Change email for user {} to {} \n'
        click.echo(green(msg.format(user.email, new_email)))


@cli.command(name='role-create')
@click.option('--handle', type=str, prompt=True, confirmation_prompt=True)
@click.option('--title', type=str, prompt=True)
@click.option('--description', type=str, prompt=True)
def create_role(*_, **kwargs):
    """ Create user role """
    click.echo(green('\nCreating new role:'))
    click.echo(green('-' * 40))

    with get_app().app_context():
        role = Role(**kwargs)
        result = role_service.save(role)
        if not isinstance(result, Role):
            print_validation_errors(result)

        click.echo(green('Created: ') + str(role) + '\n')


@cli.command(name='roles-list')
def list_roles():
    """ List existing roles """
    click.echo(green('\nListing roles:'))
    click.echo(green('-' * 40))
    with get_app().app_context():
        roles = Role.query.all()
        if not roles:
            click.echo(red('No roles found'))
            return

        for index,role in enumerate(roles):
            click.echo('{}. {}: {}'.format(
                index + 1,
                yellow(role.handle),
                role.title
            ))

    click.echo()


@cli.command(name='user-roles-list')
@click.option('--user_id', type=int, default=None, prompt=True)
def list_user_roles(*_, user_id):
    """ List user roles """
    click.echo(green('\nListing user roles:'))
    click.echo(green('-' * 40))
    with get_app().app_context():
        user = find_user(dict(id=user_id))
        if not user:
            click.echo(red('User not found\n'))
            return

        for index,role in enumerate(user.roles):
            click.echo('{}. {}: {}'.format(
                index + 1,
                yellow(role.handle),
                role.title
            ))

    click.echo()


@cli.command(name='role-add')
@click.option('--user_id', type=int, default=None, prompt=True)
@click.option('--role_handle', type=str, prompt=True)
def add_role(*_, role_handle=None, user_id=None):
    """ Add role to user """
    click.echo(green('\nAdding role to user:'))
    click.echo(green('-' * 40))
    with get_app().app_context():
        user = find_user(dict(id=user_id))
        if not user:
            click.echo(red('User not found\n'))
            return

        role = role_service.first(handle=role_handle)
        if not role:
            click.echo(red('No such role ({})\n'.format(role_handle)))
            return

        user_service.add_role_to_user(user, role)
        msg = 'Added role "{}" to user "{}"'.format(role.handle, user.email)
        click.echo(green(msg))
        return


@cli.command(name='role-remove')
@click.option('--user_id', type=int, default=None, prompt=True)
@click.option('--role_handle', type=str, prompt=True)
def remove_role(*_, role_handle=None, user_id=None):
    """ Remove role from user """
    click.echo(green('\nRemoving role from user:'))
    click.echo(green('-' * 40))
    with get_app().app_context():
        user = find_user(dict(id=user_id))
        if not user:
            click.echo(red('User not found\n'))
            return

        remove_role = None
        for role in user.roles:
            if role.handle == role_handle:
                remove_role = role

        if not remove_role:
            click.echo(red('User does not have such role\n'))
            return

        user_service.remove_role_from_user(user, remove_role)
        msg = 'Role "{}" removed from user "{}"\n'.format(
            remove_role.handle,
            user.email
        )
        click.echo(green(msg))
        return

