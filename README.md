# Refactored_CIT


## Development

### Database Management

#### Setup
 ```sh
 set PGUSER=postgres
 set PGPASSWORD=password
 ```
#### Dump
 To dump the CIT database into a SQL-script file under user postgres:
 ```sh
 $ pg_dump -U postgres cit_database > cit_backup.sql
 ```
#### Restore
 To reload a dump script into a (newly created) recovery database under user postgres:
 ```sh
 $ psql -U postgres -d cit_recovery -f cit_backup.sql
 ```

#### Push to Heroku
##### On Windows

Create a dump file:
 ```sh
 $ pg_dump -U postgres -F c -c -O cit_seed > cit_new.sql
 ```
 Use the dump file to create the Heroku database:
 ```sh
 $ set PGUSER=heroku_username
 $ set PGPASSWORD=heroku_password
 $ pg_restore -h ec2-3-211-228-251.compute-1.amazonaws.com -d d7r5ouk3pjk073 < cit_new.sql
 ```
 For more details, please refer to https://gist.github.com/michaeltreat/c04e69ebd7a85eee15a29c8ea19c8d44

##### On Mac



### Test Run

#### Windows Powershell
 Run
 ```sh
 .venv/Scripts/Activate.ps1
 ```
 Then
 ```sh
 python -m flask run
 ```
 
 To avoid the error: _Activate.ps1 cannot be loaded because running scripts is disabled on this system. For more information, see about_Execution_Policies at https:/go.microsoft.com/fwlink/?LinkID=135170_

 Run
 ```sh
 Set-ExecutionPolicy Unrestricted -Scope Process
 ```

#### Mac


### Deployment
 Prerequisite: Install Heroku CLI
 For more detailed information, please refer to https://devcenter.heroku.com/articles/git

#### GitHub
 Link to GitHub repo and enable automatic deployment

#### Manually From Windows
 First things first:
 ```sh
 heroku login
 ```
 Then create a new app for deployment:
 ```sh
 heroku create
 ```
 Or connect to an existing app:
 ```sh
 heroku git:remote -a app-name
 ```
 Rename the remote alias:
 ```sh
 git remote rename heroku cit
 ```
 Deploy to Heroku (main or master branch):
 ```sh
 git push cit main
 ```

#### Manually From Mac

