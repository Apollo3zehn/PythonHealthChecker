# Python Health Checker

The python health checker is a small app which regularly executes user-defined checks and optionally sends e-mail notifications when these checks fail. It makes it very easy to configure and extend it with new health checks.

![Health Checker](doc/app.png)

## 1 Prerequisites
- CherryPy
- aiohttp
- psutil (for the windows-service checker, optional)

## 2 What happens on failed checks?

If the built-in smtp notifier is configured (see [testconfig.conf](testconfig.conf)) and a check fails twice in a row, a mail is sent to the configured recipient. To avoid spamming mails when the state changes frequently, the notification frequency is throttled to one notification per day and per check.

## 3 How it works

### 3.1 Introduction
In its default configuration, the app runs the checks every minute. A full check cycle consists of the following steps:
- load the checker extensions (e.g. ping) and notifier extensions (e.g. smtp / e-mail)
- execute all checks and collect their results (success vs. warning vs. error)
- pass the failed check results to the configured notifiers
- write the results into a static html file

The app uses ```cherrypy``` to serve the generated html file and other static resources to the browser. The html file contains a very small javascript snippet to reload the web-page automatically every few seconds.

### 3.2 Run it yourself
To get started, clone this repo and start the app using python:

```ps
git clone https://github.com/Apollo3zehn/PythonHealthChecker
python ./Main.py
```

This will run the app with default settings, i.e:
- listen on address http://localhost:80
- browser refresh every 15 seconds
- one check per minute
- load the test config file ```testconfig.conf```

You can override the defaults by passing one or more of the following arguments to python:
```ps
python ./Main.py --host 0.0.0.0 --port 8080 `
                 --check-interval 300 `
                 --refresh-interval 60 `
                 --config myconfig.conf
```

### 3.3 Create your own config

The sample configuration (```testconfig.conf```) is part of this project and only intended for testing purposes.

It is recommended to create your own configuration file and pass the path to the app via ```--config <path to my config>```. This file should start with the shown ```# notifications``` section to setup the smtp / e-mail notification. This section is optional and only required when you would like to get notified by mail:

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

No matter if you have a ```# notifications``` section or not, the configuration file should contain a ```# checks``` section to configure all desired checks. In the sample configuration below, the first check is a ping to address ```www.test.org``` and the second check ensures that a certain windows service is available and started.

```ini
# checks
[Group 1]
type = ping-v4
notifiers = my-notifier
address = www.test.org

[Group 1]
type = windows-service
notifiers = my-notifier
name = SysMain
```

The line ```[Group 1]``` denotes the group name to help combining multiple checks into related units as you can see in the screenshot above.

Both checks refer to the previously defined notifier named `my-notifier`. Whenever the check fails it is notified to all configured notifiers. You can comma-separate multiple notifiers like `my-notifer-1, my-notifier-2, ...`.

When your configuration file is complete, you can pass it to the app: ```--config <path to my config>```

> **NOTE:**  When you update the configuration file at runtime, it is applied automatically during the next health check.

## 4 Create your own checker extension
If you need other checkers, you can implement them yourself easily. Here is an example how a very simple checker could look like:

```python
from typing import Dict

from ..BaseTypes import Checker, CheckResult

class SampleChecker(Checker):
    Type: str = "sample-checker"
    MyOption1: str

    def __init__(self, settings: Dict[str, str]):
        super().__init__(settings)
        self.MyOption1 = settings["my-option1"]
        self.MyOption2 = settings["my-option2"]

    def GetName() -> str:
        return "SampleChecker"

    async def DoCheckAsync(self) -> CheckResult:
        if self.MyOption1 == "some value":
            return self.Success()
        elif self.MyOption1 == "some other value":
            return self.Warning(f"Attention, value '{self.MyOption1}' might harm you.")
        else:
            return self.Error(f"The value '{self.MyOption1}' is invalid.")

```

Make sure your class inherits from ```Checker``` and calls the base class constructor (```super().__init__(settings)```). You can use the ```settings``` dictionary to get access to the options in the config file.

The methods ```GetName()``` and ```DoCheckAsync()``` are required and called by the base class when the check is executed.

On a successful check you can either return ```self.Success()``` or ```self.Success(<your success message>)```. When the check fails, return ```self.Error(<your error message>)``` instead.

When you are done, copy the new python file into the ```./src/Extensions``` folder. You should not (re)start the app to ensure the new extensions gets loaded. Alternatively, it will be loaded automatically during the next check cycle.

With your new checker in place, you should update your configuration file like this to define one or multiple checks:

```ini
# notifications
...

# checks
[My Group]
type = sample-checker
notifiers = my-notifier
my-option1 = some value
my-option2 = some value

[My Group]
type = sample-checker
notifiers = my-notifier
my-option1 = some value
my-option2 = some value

...
```

Please see the [testconfig.conf](testconfig.conf) file for a full sample.

## 5 Create your own notifier extension
If you need another notifier instead of smtp, the process is similar to that of the checker extension.

```python
import os
from typing import Dict, List

from ..BaseTypes import CheckResult, Notifier


class SampleNotifier(Notifier):
    Type: str = "sample-notifier"
    MyOption1: str
    MyOption2: str

    def __init__(self, settings: Dict[str, str]):
        super().__init__(settings)

        self.MyOption1 = settings["my-option1"]
        self.MyOption2 = settings["my-option2"]

    async def NotifyAsync(self, checkResult: Dict[str, List[CheckResult]]):

        # The following is a sample of how to construct a string message from
        # all checks, which are contained in the checkResult variable.

        # 1. Get a notifcation message for each check group
        contents = [self._getGroupContent(group, checkResults) for (group, checkResults) in result.items()]
        message = "\n".join(contents)

        # 4. notify everyone that wants to be notified
        # sending 'message' ...
        
    def _getGroupContent(self, group: str, checkResults: List[CheckResult]) -> str:

        # 2. Get a notifiations message for each check result within the group
        contents = [self._getContent(checkResult) for checkResult in checkResults]
        message = group + "\n" +  "\n".join(contents)

        return message

    def _getContent(self, checkResult: CheckResult) -> str:
        return f"{checkResult.Name}: {checkResult.Message}"
```

Make sure your class inherits from ```Notifier``` and calls the base class`s constructor (```super().__init__(settings)```). You can use the ```settings``` dictionary to get access to the options in the config file.

The method ```NotifyAsync()``` is required and called by the base class when the notifiers are executed. The other methods are only there to help constructing a readable message from the check result.

When you are done, copy the new python file into the ```./src/Extensions``` folder. If you are not restarting the app, it will instead be (re)loaded automatically during the next check cycle.

With your new notifier in place, you should update your configuration file like this to define one or multiple notifications:

```ini
# notifications
[my-notifier]
type = sample-notifier
my-option1 = some value
my-option2 = some value

[my-notifier]
type = sample-notifier
my-option1 = some other value
my-option2 = some other value

...

# checks
...
```

## 6 External checks

It may become necessary to make checks on another device and send the results to the health checker instance. For these cases, a REST API is available at `http://<health-checker-address>/api/checkresults`. You can use any program or script to push check results to the health checker. 

### 6.1 Powershell
For example using `powershell`:

```powershell
# First, do your checks. Then send them to the health checker:

$checkResult = @{
    identifier  = "MyIdentifier" # explained below
    name        = "The title of my check."
    message     = "The check has been successful"
    resultType  = 1 # 1 = Success, 2 = Warning, 3 = Error
}

$targetHostName = 'http://<health-checker-address>'

# send the result to the health checker
Invoke-RestMethod `
    -Uri "$targetHostName/api/checkresults" `
    -Method POST `
    -Body ($checkResult | ConvertTo-Json -Depth 3) `
    -ContentType 'application/json'
```

The `identifier` is a unique string to identify the check result. The health checker will only pick up check results with known identifiers. To make these known to the health checker, configure a new check of type `external-cache` and provide the `identifier` and `max-age-minutes` values:

```ini
# checks
[Group 1]
type = external-cache
identifier = MyIdentifier
max-age-minutes = 10
```

### 6.2 Second Health Checker

#### 6.2.1 Push
It is also possible to run a second health checker and push its result to the main health checker. In that case define the `external-cache` check(s) as described previously in your main health checker and then just add the following values to any check in the second health checker that should share its result:

```ini
# checks
[Group 1]
type = ping-v4
...
share-method = http-post
share-target = http://<main-health-checker-address>/api/checkresult
share-id = "MyIdentifier"
```

___
Please see the [testconfig.conf](testconfig.conf) file for a full sample.

#### 6.2.2 Pull
If pushing is not possible, pull is another way to get the data. In your second health checker add a check entry like this:

```ini
type = <any type>
identifier = <unique-identifier>
<more properties> = ...
```

And in your main health checker, use the unique identifier specified before and set the url to the second health checker:

```ini
type = query-federated
url = http://localhost:8080
remote-identifier = <unique-identifier>
```