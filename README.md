# bb_change_broker

## Description

bb_change_broke is a Python tool that offers a server and client to send changes from different SCM repositories via hooks and a resilient message queue to a buildbot master.

Idea:

  * Git repository -> post-commit hook -> bb_change_broker client -> RabbitMQ -> bb_change_broker server -> buildbot master
  * SVN repository -> post-commit hook -> bb_change_broker client -> RabbitMQ -> bb_change_broker server -> buildbot master

## Installation

  1. For each machine, you will need to install bb_change_broker. Afterward, you can run it with the command bb_change_broker.

      ```bash
      cd bb_change_broker
      python setup.py install
      ```

  2. In your SVN repo, create a file hooks/post-commit with the following content:

      ```bash
      #!/bin/sh
      bb_change_broker /srv/svn/repository/hooks/config.json
      ```

  3. In your Git repo, create a file hooks/post-receive with the following content:

      ```bash
      #!/bin/sh
      bb_change_broker /srv/git/repository/hooks/config.json
      ```

  4. Setup RabbitMQ and set up a user that you can use for the client and server.

  5. Install the server on the buildbot master or some other machine that can access the buildbot master.

  6. Run the server as service with automatic restarts. On Ubuntu, for example, you do the following:
    
      ```bash
      sudo cp bb_change_broker/server/bb_change_broker /etc/init.d/
      sudo update-rc.d bb_change_broker defaults
      sudo service bb_change_broker start
      ```

  7. In your buildbot master configuration, you need to add a custom change hook 

      ```python
      class CustomWebhook(webhooks.base):
        def getChanges(self, request):
            data = request.content.read()
            args = json.loads(data.decode("utf-8"))
            chdict = args[0]
            log.msg("Got change: %s" % chdict)
            return ([chdict], None)
      ```

  8. Then add the class to your base dialect.

      ```python	
      change_hook_dialects={
          "base": {
              "custom_class": CustomWebhook,
          },
      },
      ```

  9. Finally, reconfigure buildbot.

  10. You can now see the latest changes coming in via RabbitMQ on http://localhost:8010/#/changes.

## Configuration

### DEFAULT

The default configuration of the .json file offers general settings.

  * mode: client or server
  * encoding: The encoding of machine. Default is utf-8.

    ```json
      "DEFAULT": {
        "mode": "client",
        "encoding": "utf-8"
      }
    ```

### Logging

The logging configuration is optional. If you do not specify it, then the logger is disabled.

The syntax follows the built-in Python logging module dictionary config, also see https://docs.python.org/3/library/logging.config.html. 

To specify the logging configuration, you need to add a section called "logging" and follow the specification of the logging module.

```json
"logging": {
        "version": 1,
        "disable_existing_loggers": false,
        "formatters": {
            "console": {
                "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
            }
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "console",
                "filename": "/data/bb_change_broker.log",
                "maxBytes": 102400,
                "backupCount": 10
            }
        },
        "loggers": {
            "": {
                "handlers": [
                    "file"
                ],
                "level": "DEBUG"
            }
        }
    },
```

### Change sources

If you are using the module as client, then you need to specify exactly one change source.

#### Git

In the case of Git, you have the following options:

  * repository: The path to the repository.

```json
  "git": {
    "repository": "/srv/git/project.git"
  }
```

#### SVN

For SVN, you have the following options:

  * repository: The path to the repository.
  * branch_filters: A list of filters to extract branch and file name. 
  
    * The first element is a list of parts of the total path that will be matched. A minus in front of a part means unequal.
    * The second element is the start index of the branch name.
    * The third element is the end index -1 of the branch name.

    ##### Examples
    
    * Filter: [["root", "trunk", "-php"], 1, 2]
    * Path: /root/trunk/php/file1.php
    * -> Branch: "", File: root/trunk/php/file1.php
    ----
    * Filter: [["root", "trunk", "php"], 1, 3]
    * Path: /root/trunk/php/file1.php
    * -> Branch: trunk/php, File: file1.php
    ----
    * Filter: [["root", "trunk", "php"], 1, 2]
    * Path: /root/trunk/notphp/file1.php
    * -> Branch: "", File: root/trunk/php/file1.php
    ----
    It is possible to have multiple filters. The first filter that matches will be used. If no filter matches, then the branch will be empty and the file will be the full path.
  

```json
  "svn": {
    "repository": "/srv/svn/repository",
    "branch_filters": [
      [["root", "trunk", "-php"], 1, 2],
      [["root", "branches", "device"], 1, 5]
    ]
  }
```

### Broker

In both server and client mode, you need to configure the broker.

  * host: The host of RabbitMQ.
  * port: The port of RabbitMQ.
  * username: The username for RabbitMQ.
  * password: The password for RabbitMQ.
  * queue: The queue name.

```json
"rabbitmq": {
  "host": "rabbitmq",
  "port": 5672,
  "username": "guest",
  "password": "guest",
  "queue": "hello"
}
```

### Buildbot

In both server and client mode, you need to specify the credentials for buildbot. This is because the client will send the changes to the buildbot master directly if the broker is not available.

  * host: The host of buildbot.
  * port: The port of buildbot.
  * username: The username for buildbot.
  * password: The password for buildbot.

```json
  "buildbot": {
      "host": "buildbot",
      "port": 8010,
      "username": "user",
      "password": "pass"
    }
```

## Basic Authentication for Buildbot

If you want to use basic authentication for buildbot, then you need to proceed as in step 8 above, but in your www config, you need to add the following:

```python
from twisted.cred import strcred
c['www'] = dict(...,
      change_hook_auth=[strcred.makeChecker("file:changehook.passwd")],
)
```

Afterward, create a file called changehook.passwd with the following content:

```bash
user:password
```

## Testing

### Unit Tests

Run the unit tests with the built-in module unittest.

```bash
python -m unittest discover .
```

or install coverage and run the tests with coverage.

```bash
coverage run --source=bb_change_broker -m unittest discover . 
coverage report -m
```

They offer mocks for most of the modules that use external resources and provide a good coverage to spot some minor bugs.

## FAQ

### Multiple Buildbot Masters

At the moment, the module does not support defining multiple masters. However, you can do the following:

  1. Run a server for each master
  2. Each server needs a separate queue in the broker
  3. In the post-commit and post-receive hooks, you call bb_change_broker for each master
  4. For each method call, define a different config file with the queue and credentials for the master.
