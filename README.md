#  Terminal Watcher server
To use heroku:
1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli#download-and-install).

To start locally:
1. Install [pipenv](https://pipenv.pypa.io/en/latest/).
1. Clone this repo
1. `cd path/to/terminal-watcher`
1. `pipenv shell`
1. `set -o allexport; source .env; set +o allexport`
1. `flask run`
1. To point the app in emulator: 
   1. `adb shell setprop com.terminalwatcher.android.base_url http://10.0.2.2:5000` (`10.0.2.2` [is the host](https://stackoverflow.com/questions/5528850/how-do-you-connect-localhost-in-the-android-emulator) and `5000` is Flask's default port)
   1. `adb shell setprop com.terminalwatcher.android.account brufino`

Useful:
* See logs with heroku: `heroku logs --tail`
* [Debug production](https://terminal-watcher.herokuapp.com/)
* If not getting FCM messages, may need to uninstall & install in device to register
* Python version doesn't match? Update `runtime.txt` ([for heroku](https://devcenter.heroku.com/articles/python-runtimes)) and `Pipfile`.