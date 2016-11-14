import click
import os
import subprocess
from jinja2 import Environment, FileSystemLoader

NGINX_CONFIG_PATH = '/etc/nginx/apps.d'
GIT_PATH = '/opt/serve'
APP_PATH = '/home/serve/apps'
AUTHORIZED_KEYS = '/home/serve/.ssh/authorized_keys'


env = Environment(loader=FileSystemLoader('/home/serve/serve/serve/templates'))

def write_nginx_config(app_name):
    """
    Write the NGINX config for the app.
    """

    docker_port = subprocess.check_output(['docker', 'port', app_name]).strip()[-5:]

    template = env.get_template('nginx_app.conf')
    return template.render(app=app_name, docker_port=docker_port)

def configure_git_hooks(app_name, git_path):
    """
    Create the post-receive hook to build the docker image for the app.
    """
    template = env.get_template('post-receive')
    return template.render(app=app_name, git_path=git_path)

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
    with open(AUTHORIZED_KEYS, 'r') as f:
        for line in f:
            click.echo(line[line.index('== ') + 3:])

@user.command(help="Add a new user's SSH key to Serve.")
@click.argument('key')
def add(key):
    """
    Add a new user's SSH key to Serve
    """
    if key.startswith('ssh-rsa'):
        user = key[key.find('== ') + 3:]
        with open(AUTHORIZED_KEYS, 'a') as f:
            f.write(key)
        click.echo("Added SSH key for {} to authorized keys.".format(user))
    else:
        click.echo("The provided key does not appear to be valid.")

@user.command(help="Remove a user's access to Serve.")
@click.argument('user')
def remove(user):
    """
    Remove a user's access to Serve.
    """
    click.echo("Removing key for {}".format(user))
    subprocess.call(["sed", "--in-place", '/{}/d'.format(user), AUTHORIZED_KEYS])

@serve.group(help="Commands for app management.")
def app():
    pass

@app.command(name='list', help="List all apps.")
def list_apps():
    """
    List all apps that have been created in Serve.
    """
    click.echo("All apps:")
    click.echo("\n".join(os.listdir(APP_PATH)))

@app.command(help="Create a new app to Serve.")
@click.argument('app')
def new(app):
    """
    Create a new app.
    """
    click.echo("Creating the {} app.".format(app))
    app_git_path = os.path.join(GIT_PATH, '{}.git'.format(app))
    os.mkdir(app_git_path)
    os.chdir(app_git_path)
    subprocess.call(['git', 'init', '--bare'])
    with open(os.path.join(app_git_path, 'hooks', 'post-receive'), 'w') as f:
        f.write(configure_git_hooks(app, app_git_path))
    subprocess.call(['chmod', '+x', os.path.join('hooks', 'post-receive')])

    click.echo("Created {} app with remote url {}.".format(app, app_git_path))

@app.command(help="Delete a Serve app.")
@click.argument('app')
def delete(app):
    """
    Delete an app.
    """
    click.echo("Deleting the {} app.".format(app))
    subprocess.call(['rm', '-rf', os.path.join(GIT_PATH, "{}.git".format(app))])
    subprocess.call(['rm', '-rf', os.path.join(APP_PATH, app)])
    subprocess.call(['rm', os.path.join(NGINX_CONFIG_PATH, "{}.conf".format(app))])
    subprocess.call(['docker', 'stop', app])
    subprocess.call(['docker', 'rm', app])
    subprocess.call(['docker', 'rmi', "{}-image".format(app)])

@app.command(help="Display information about a running application.")
@click.argument('app')
def info(app):
    """
    Display information about a running application.
    """
    click.echo("Info for {}.".format(app))
