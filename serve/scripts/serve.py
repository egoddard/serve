import click
import os
import subprocess
from collections import namedtuple
from jinja2 import Environment, FileSystemLoader

Urls = namedtuple('Urls', ['fqdn', 'git'])

NGINX_CONFIG_PATH = '/etc/nginx/apps.d'
GIT_PATH = '/opt/serve'
APP_PATH = '/home/serve/apps'
AUTHORIZED_KEYS = '/home/serve/.ssh/authorized_keys'
try:
    with open('/home/serve/.urls', 'r') as f:
        urls = f.read().strip().split()
        URLS = Urls(urls[0], "ssh://serve@{}:{}".format(urls[1], urls[2]))
except IOError:
    URLS = Urls('localhost:8080', 'ssh://serve@localhost:2222')


env = Environment(loader=FileSystemLoader('/home/serve/serve/serve/templates'))

def write_nginx_config(app):
    """
    Write the NGINX config for the app.
    """

    docker_port = subprocess.check_output(['docker', 'port', app]).strip()[-5:]

    template = env.get_template('nginx_py.conf')
    with open(os.path.join(NGINX_CONFIG_PATH, "{}.conf".format(app)), 'w') as f:
        f.write(template.render(app=app, docker_port=docker_port))

def configure_git_hooks(app, git_path):
    """
    Create the post-receive hook to build the docker image for the app.
    """
    template = env.get_template('post-receive')
    return template.render(app=app, git_path=git_path)

@click.group()
def serve():
    pass

@serve.command(name='set-url', help="Set the url and port of the server.")
@click.argument('fqdn')
@click.option('--port', default=22, help="The port to use for SSH.")
def seturls(fqdn, port):
    with open('/home/serve/.urls', 'w') as f:
        f.write("{},{}".format(fqdn, port))

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
    apps = [app[:-4] for app in os.listdir(GIT_PATH)]
    click.echo("\n".join(apps))

@app.command(help="Create a new app to Serve.")
@click.argument('app')
def create(app):
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

    click.echo("Created {} app with remote url {}{}".format(app, URLS.git,
        app_git_path))

@app.command(help="Delete a Serve app.")
@click.argument('app')
def delete(app):
    """
    Delete an app.
    """
    click.echo("Deleting the {} app.".format(app))
    try:
        subprocess.call(['rm', '-rf', os.path.join(GIT_PATH, "{}.git".format(app))])
    except subprocess.CalledProcessError:
        click.echo("{} does not exist, skipping.".format(os.path.join(GIT_PATH, "{}.git".format(app))))
    try:
        subprocess.call(['rm', '-rf', os.path.join(APP_PATH, app)])
    except subprocess.CalledProcessError:
        click.echo("{} does not exist, skipping.".format(os.path.join(APP_PATH, app)))

    try:
        subprocess.call(['rm', os.path.join(NGINX_CONFIG_PATH, "{}.conf".format(app))])
    except subprocess.CalledProcessError:
        click.echo("{} does not exist, skipping.".format(os.path.join(NGINX_CONFIG_PATH, "{}.conf".format(app))))

    try:
        subprocess.call(['docker', 'stop', app])
        subprocess.call(['docker', 'rm', app])
    except subprocess.CalledProcessError:
        click.echo("Docker app {} does not exist, skipping...".format(app))

    try:
        subprocess.call(['docker', 'rmi', "{}-image".format(app)])
    except subprocess.CalledProcessError:
        click.echo("Docker image {}-image does not exist, skipping...".format(app))

@app.command(help="Start an app.")
@click.argument('app')
def start(app):
    """
    Start the container for the app.
    """
    click.echo("Starting the {} container...".format(app))
    subprocess.call(['docker', 'start', app])

    # Rewrite the nginx config to update the port
    write_nginx_config(app)
    subprocess.call(['sudo', '/etc/init.d/nginx', 'reload'])

@app.command(help="Stop an app.")
@click.argument('app')
def stop(app):
   """
   Stop the container for the app."
   """
   click.echo("Stopping the {} container...".format(app))
   subprocess.call(['docker', 'stop', app])

@app.command(help="Display information about a running application.")
@click.argument('app')
def info(app):
    """
    Display information about a running application.
    """
    app_git_path = os.path.join(GIT_PATH, '{}.git'.format(app))
    docker_port = subprocess.check_output(['docker', 'port', app]).strip()
    running = app in subprocess.check_output(['docker', 'ps'])
    if running:
        click.echo("Info for {} [running]:".format(app))
    else:
        click.echo("Info for {} [stopped]:".format(app))

    click.echo("Git URL: {}{}".format(URLS.git, app_git_path))
    click.echo("URL: {}/{}".format(URLS.fqdn, app))
    click.echo("Mapped Ports: {}".format(docker_port))

