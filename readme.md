# Setup

### Google App Setup (sorta)

1. Create a New Google App Project [here](https://console.cloud.google.com/projectcreate)
2. Check to see if Oauth is enabled [here](https://console.cloud.google.com/apis/credentials)
    1. If Oauth is not enabled, edit the app [here](https://console.cloud.google.com/apis/credentials/consent)
    2. On the same page, while editing the app, click '*save and continue*'
4. Now add the following api scopes to your project if they are not already added
```
auth/user.birthday.read
auth/tasks
auth/drive
auth/drive.file
auth/documents
auth/calendar
auth/calendar.events
```
5. Click '*save and continue*'
6. If you would like multiple people to use your app, select '*+ add users*'
    1. Fill out the required user information
    2. Click '*save and continue*'
7. If the summary of the app looks good, then return to dashboard, otherwise, make necessary changes.

### Environmental Variables

**Linux**

```bash
export FN_AUTH_REDIRECT_URI = "http://HOST:PORT/google/auth"
export FN_BASE_URI = "http://HOST:PORT"
export FN_CLIENT_ID = "ID.apps.googleusercontent.com"
export FN_CLIENT_SECRET = "SECRET"
export FLASK_APP = "betteryear.py"
export FLASK_DEBUG = 1
export FN_FLASK_SECRET_KEY = "develdev"
```

**Windows**

```powershell
$env:FN_AUTH_REDIRECT_URI = "http://HOST:PORT/google/auth"
$env:FN_BASE_URI = "http://HOST:PORT"
$env:FN_CLIENT_ID = "ID.apps.googleusercontent.com"
$env:FN_CLIENT_SECRET = "SECRET"
$env:FLASK_APP = "betteryear.py"
$env:FLASK_DEBUG = 1
$env:FN_FLASK_SECRET_KEY = "develdev"
```