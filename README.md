# Python Health Checker

The python health checker is a small app which regularly executes user-defined checks and optionally sends e-mail notifications on error. It makes it very easy to configure it and extend it with new health checks.

#### Web-UI
![Health Checker](doc/app.png)

#### Prerequisites
- CherryPy
- psutil

#### What happens on failed checks?

If the smtp notifier is configured, a mail is sent to the configured recipient. To avoid spamming mails when the state changes frequency, the notification frequency is throttled to one notification per day and per check.

#### How it works

##### Introduction
In its default configuration, the app runs the checks every minute. A check consists of the following steps:
- load the checkers (e.g. ping) and notifiers (e.g. smtp / e-mail)
- execute all checks and collect their results (success or error)
- pass the results to the configured notifiers
- write the result into an html file

The app uses ```cherrypy``` to serve the generated html file and other static resources to the browser. The html file contains a very small javascript snippet to reload the web-page automatically every few seconds.

##### Run it yourself
To get started, clone this repo and start the app using python:

```ps
git clone https://github.com/Apollo3zehn/PythonHealthChecker
python ./Main.py
```

This will run the app with default settings, i.e:
- listen on address http://localhost:80
- one check per minute
- test configuration file ```testconfig.conf```

You can override the defaults by passing one or more arguments to python:
```ps
python ./Main.py --host 0.0.0.0 --port 8080 `
                 --interval 300 --config myconfig.conf
```

##### Create your own config
The app uses a simple config file, which should start with a ```# notifications``` section to setup the smtp / e-mail notification. This section is optional and only required when you would like to get notified by mail.

```ini
# notifications
[my-notifier]
type = smtp
security = starttls
server = xxx.net
port = 587
password = xxx
from = xxx@yyy.net
to = zzz@aaa.net
subject = Health-Check Report
```

The second section (```# checks```) contains all desired checks. The first one is a ping check pointing to address ```www.test.org```.

The second check ensures that a certain windows service is available and started.

```ini
# checks
[Group 1]
type = ping-v4
notifiers = test
address = www.test.org

[Group 1]
type = windows-service
notifiers = test
name = SysMain
```

The line ```[Group 1]``` represents the group name to help combining multiple checks into related units.

Both checks refer to the previously defined notifier named `my-notifier`.

To apply you custom config, pass the file path to the app, e.g: ```python ./Main --config <config file>```

> **NOTE:**  When you update the configuration file at runtime, it is applied automatically during the next health check.

##### Create your own checker
If you need other checkers, you can implement it yourself easily. Here is an example how a checker could be implemented:

```python
import os
from typing import Dict

from ..BaseTypes import Checker, CheckResult

class FakeChecker(Checker):
    Type: str = "fake-checker"
    Option1: str

    def __init__(self, settings: Dict[str, str]):
        super().__init__(settings)
        self.Address = settings["option1"]

    async def DoCheckAsync(self) -> CheckResult:
        if option1 == "value1":
            return self.Success(option1)
        else:
            return self.Error(option1, f"The value '{option1}' is invalid.")

```

Make sure your class inherits from ```Checker``` and calls the base class`s constructor (```super().__init__(settings)```). You can use the ```settings``` dictionary to get access to the options in the config file.

tbd ...


