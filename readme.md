Make a cronjob for daily of the following command:  
==> python manage.py flushexpiredtokens

this command will flush all the blacklisted token

Read cookie. this will be the first api to be called on every refresh..
It will give "access token" on every refresh which will set the token in frontend
and let the frontend know if the user need to login or not nad the current token is valid or invalid.
frontend should put check on the object backend send:

if status = 1 <------|
then backend give new access token |
if status = 0 |  
 then user need to login again |  
if status = 2 |  
 then the same access token will be send <-----|

api url ==> "/read_cookie"

Install Redis for your system

then run the following command in project directory
celery -A lyne worker -l info
&
redis-server
