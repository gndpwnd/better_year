# Setup

### Google App Setup (sorta)

1. Create a New Google App Project [here](https://console.cloud.google.com/projectcreate)
2. Check to see if Oauth is enabled [here](https://console.cloud.google.com/apis/credentials)
    1. If Oauth is not enabled, edit the app [here](https://console.cloud.google.com/apis/credentials/consent)
    2. On the same page, while editing the app, click '*save and continue*'
4. Now add the following api scopes to your project if they are not already added
    1. auth/user.birthday.read
    2. auth/tasks
    3. auth/drive
    4. auth/drive.file
    5. auth/documents
    6. auth/calendar
    7. auth/calendar.events
5. Click '*save and continue*'
6. If you would like multiple people to use your app, select '*+ add users*'
    1. Fill out the required user information
    2. Click '*save and continue*'
7. If the summary of the app looks good, then return to dashboard, otherwise, make necessary changes.