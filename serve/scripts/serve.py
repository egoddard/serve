import click

@click.group()
def serve():
    pass

@serve.group(help="Commands for user management.")
def user():
    pass

@user.command(name='list', help="List users")
def list_users():
    """
    List all users that have permission to manage Serve
    """
    click.echo("Users:")

@user.command(help="Add a new user's SSH key to Serve.")
@click.argument('key')
def add(key):
    """
    Add a new user's SSH key to Serve
    """
    click.echo("Adding key {}".format(key))

@user.command(help="Remove a user's access to Serve.")
@click.argument('user')
def remove(user):
    """
    Remove a user's access to Serve.
    """
    click.echo("Removing key for {}".format(user))

@serve.group(help="Commands for app management.")
def app():
    pass

@app.command(name='list', help="List all apps.")
def list_apps():
    """
    List all apps that have been created in Serve.
    """
    click.echo("All apps:")

@app.command(help="Create a new app to Serve.")
@click.argument('app')
def new(app):
    """
    Create a new app.
    """
    click.echo("Creating the {} app.".format(app))

@app.command(help="Delete a Serve app.")
@click.argument('app')
def delete(app):
    """
    Create a new app.
    """
    click.echo("Creating the {} app.".format(app))

@app.command(help="Display information about a running application.")
@click.argument('app')
def info(app):
    """
    Display information about a running application.
    """
    click.echo("Info for {}.".format(app))
