

.. role:: bash(code)
   :language: bash

.. |serve_cli| image:: serve_cli.png

=====
Serve
=====

Eric Goddard

COMP 4272 Project 

Objective
---------

Serve is a tool for managing Docker-based web apps on a web server. It allows
users to use a Git-based workflow to deploy and update web apps by configuring
an additional remote to push to, hosted on the web server. Once pushed, Serve
builds the Docker image according to the Dockerfile included with the project
and configures NGINX to serve as a reverse proxy so that the new web app is
accessible as an endpoint on the web server. For example, if the server's
hostname is example.com, and the web app is named webmap, The app could be
viewed by visiting example.com/webmap.


Description
------------

Serve runs on Ubuntu 14.04 servers. The CLI interface is written in Python, and
uses both Python and Bash to execute the commands. The CLI allows the user to:

    * List users
    * Delete users
    * Create users
    * List apps
    * Create apps
    * Delete apps
    * Stop an app's Docker container
    * Start an app's Docker container
    * Display information about an app, such as:
        * whether it is running
        * URL
        * Git URL
        * Mapped ports

Serve can be installed by running the install script.
If the user has an existing Ubuntu 14.04 web server, clone the repository
onto the server as a user with sudo rights, then run :bash:`sudo ./install.sh`.
Otherwise, a Vagrantfile is included that will
setup an Ubuntu 14.04 VM and install Serve. Install Vagrant if necessary, and
then start it by typing :bash:`Vagrant up` in the root project directory.

The Serve installer creates a new user, named serve, under which the Serve
commands are installed and is also where the projects are stored. 
The first step after installation is to add an ssh key to Serve to give a
user remote access to manage apps and push the apps to the web server using Git.
copy the ssh key from your ~/.ssh/id_rsa.pub file and then SSH into the web
server as a user with sudo access, and then run the following
commands::

    sudo su serve
    cd
    serve user add "<paste ssh key in between the double quotes>"

With the ssh key added to the serve user, logout of the ssh session and create
a new SSH session as the serve user. You'll have access to the serve commands.
To see them, type :bash:`serve`. It will display the two commands available.
Each of the commands has subcommands, and can be used by typing
:bash:`serve <command>`.::

    serve@serve:~$ serve
    Usage: serve [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      app      Commands for app management.
      set-url  Set the url and port of the server.
      user     Commands for user management.
    serve@serve:~$ serve app
    Usage: serve app [OPTIONS] COMMAND [ARGS]...

      Commands for app management.

    Options:
      --help  Show this message and exit.

    Commands:
      create  Create a new app to Serve.
      delete  Delete a Serve app.
      info    Display information about a running...
      list    List all apps.
      start   Start an app.
      stop    Stop an app.


Create a new app by typing :bash:`serve app create <appname>`. The git repository
will be configured for the application and the remote url for the app will be
displayed. Copy the remote url and add it as another remote in the git repository
of the web app you would like to publish, and then push it to the server. Serve
will automatically rebuild the docker image and update the nginx configuration
to serve the application at http://<hostname>:<port>/<app>.

Project Details
---------------

Serve uses Docker, Bash, Python, NGINX, SSH and Git to serve the web apps. The Serve
command line interface is written in Python using the Click library. There are
two main commands, one for managing users and the other for managing apps. Each
command has additional subcommands. Vagrant is also used to automatically
configure a virtual machine running Serve, but it isn't required.

After Serve is installed, the first step is to create a user. Since the Git
server uses SSH for authentication, the Serve user commands list, add, and delete
keys from serve's authorized_keys file.

Most of Serve's functionality is in the app subcommand. When a new app is created,
a bare repository is created in /opt/serve/<app>. A post-receive hook is configured
and the Python jinja2 templating library is used to replace the **app_name** and 
**docker_port** placeholders in the serve/templates/post-receive bash script.
Since the bare repository doesn't have a HEAD reference, it can't be used directly.
The post-receive hook fires after all of the changes have been committed on the
remote side, and it then clones the app's repo from /opt/serve/<app> into a
repository at /home/serve/apps/<app>. After cloning the repo, the post-receive
script initiates a docker build (or rebuild) of the app. Docker maps any exposed
ports in the Dockerfile to a random port greater than 32768 on the host. The final
step in the post-receive script is to get the randomly assigned port number from
docker and add the reverse proxy configuration to NGINX. the post-receive script
uses sed to replace the #app# and #docker_port# occurrences in the
serve/templates/nginx_bash.conf file and copies into a configuration file in
/etc/nginx/apps.d/. The default nginx site is configured to include all
configuration files in this folder, so after reloading the nginx config the app
should be available.

The remaining app commands are pretty self explanatory. Python's subprocess
package is used to run Docker commands when the
:bash:`serve app start|stop|info <app>` commands are used. However, since Docker
maps a random port on the host machine to the exposed ports in the container,
anytime an app is restarted the nginx configuration has to be updated. The
update is done by using the the Python jinja2 library to rewrite the app's 
NGINX configuration in the /etc/nginx/apps.d folder and reloading the NGINX
configuration.

Pushing the test app to Serve
-----------------------------

After settings up Serve and adding your local ssh public key to the serve user's
authorized_keys file with the :bash:`serve user add "<key>"`, create a project
with :bash:`serve app new test-project`. The app for the test-project must be
named test-project, as it is a Django app and the urls.py has been configured to
make the app accessible at /test-project.

On your local machine, clone the test project into a new repository (outside of
the serve directory) with
:bash:`git clone https://github.com/egoddard/serve-test-project.git`.
:bash:`cd` into the serve-test-project folder. In the serve-test-project folder,
configure another remote by typing
:bash:`git remote add serve ssh://serve@localhost:2222/opt/serve/test-project.git`.
With the remote configured, type :bash:`git push serve master` to push the
project to the server. Open a browser and type in
http://localhost:8080/test-project as the URL and you should see the website.

Conclusion
----------

I chose to do this project because I use a tool called Dokku at work, which
does almost everything I implemented and many that I didn't.
While I have created many Dockerfiles to serve my apps on Dokku, I have not
had to actually use Docker or NGINX much since it was all handled by Dokku.
Creating Serve gave me a better understanding of how Docker and NGINX work, and
I learned how to use NGINX to route the apps as URL endpoints instead of
subdomains (which is how Dokku does it). For example, if the URL of my app on
Dokku is test-app.subdomain.example.com, The URL in Serve would be 
subdomain.example.com/test-app. I prefer the latter format, and if nothing else
completing Serve has helped me learn how I can customize the Dokku NGINX
configuration to serve URLS in my preferred format.

If I continue working on Serve, the next steps I would like to complete are
adding Docker Compose support for creating multi-container applications, and
adding a command to add SSL/TLS encryption using LetsEncrypt certificates.
