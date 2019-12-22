## Agestudy application
The app is built and run on IBMcloud cloudfoundry. The builtpack is python.
It connects to a DB2 instance.

# Run app locally
Set a key to your database in a file called key.txt

Set a secret_key for flask

```
FLASK_APP=application.py flask run
```

# Register
The register page asks the user for the following items:
- username (textbox)
- email (textbox)
- participating for money (checkbox)
- if they are able to collect money (checkbox)
- birthdate (date)
- gender
- password
- re-enter password

if the username, birthdate, gender, email or password and re-entered password is missing,
user cannot register. Those fields are required.

After registration redirect to home page.
![register](images/register.jpg)

- TODO : Javascript
- TODO : send email
- TODO : remove date from birthdate

# Login
Check if the username and password are correct.
Get the user information from database and set session.

If incorrect redirect user to same page and show error message
- TODO : This with Javascript
![login](images/login.jpg)
