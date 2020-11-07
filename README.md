#  Terminal Watcher server
To use heroku:
1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli#download-and-install).

To start locally:
1. Install [pipenv](https://pipenv.pypa.io/en/latest/).
1. Clone this repo
1. `cd path/to/terminal-watcher`
1. `pipenv shell`
1. `exit` to exit

Useful:
* See logs with heroku: `heroku logs --tail`
* [Debug production](https://terminal-watcher.herokuapp.com/)
* If not getting FCM messages, may need to uninstall & install in device to register
* Python version doesn't match? Update `runtime.txt` ([for heroku](https://devcenter.heroku.com/articles/python-runtimes)) and `Pipfile`.