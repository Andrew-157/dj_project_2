# DJANGO PROJECT 'Articlee'

## Articlee allows you to publish your articles with thumbnail and tags. You can read, comment, react and add to your 'favorites' articles, published by another users. You can also subscribe to other users and search for articles you are interested in.

Requirements:
```
    django
    django-crispy-forms
    django-cleanup
    crispy-bootstrap4
    django-taggit
    pillow
    mysqlclient
    django-environ
    django-debug-toolbar
    autopep8
```

## Run project

### The following steps show how to run project locally(i.e., with DEBUG=True)
**The following steps assume that you cloned project repository to your working directory**

If you are using pipenv,run in the command line from directory where Pipfile is located:
```
    pipenv install
```

To activate environment using pipenv, run in the command line in the same directory:
```
    pipenv shell
```

Generate secret key, using the following code:
```python
    import secrets

    secret_key = secrets.token_hex(32)

    print(secret_key)
```

In directory 'articlee' create file .env(**do not forget to add it to .gitignore, if it is not there**) and add the following line:
```
    SECRET_KEY=<secret_key_you_generated>
```

Then you need to create MySQL database (using MySQL Workbench or any other tool), using SQL statement:
```SQL
    CREATE DATABASE <your_database_name>;
```

Next, go to .env and using credentials of your database, add the following lines:
```
    DB_NAME=<your_database_name>
    DB_USER=<your_database_user>
    DB_PASSWORD=<your_database_password>
    DB_HOST=<your_database_host>
    DB_PORT=<your_database_port>
```

After that, in command line run:
```
    python manage.py migrate
    python manage.py runserver
```

Go to your browser at the address: 'http://127.0.0.1:8000/', you should be able to see Articlee's index page

## Admin site

If you want to visit admin site, run the following command:
```
    python manage.py createsuperuser
```

Enter credentials for your admin user, and visit 'http://127.0.0.1:8000/admin',
login using the same credentials you used when you created admin user.


## Testing

## Each app contains 'tests' directory with "__init__.py" and 3 modules(each module's name starts with test)

**Tests for articlee are written using Django's TestCase**
That means that each test module contains following import statement:
```python
    from django.test import TestCase
```
And each testing class is create like this:
```python
    class SubscriptionModelTest(TestCase):
        pass
```

If you want to run all tests available in the project, in the command line run:
```
    python manage.py test
```

Articlee has over 200 tests written, so you may want run only particular tests.

The following commands will show how to run tests of app "personal" of "articlee" project.

To run tests for whole app, use this command:
```
    python manage.py test personal
```

If you want to run only particular module from 'personal/tests', use this command:
```
    python manage.py test personal.test_views
```

If you want 