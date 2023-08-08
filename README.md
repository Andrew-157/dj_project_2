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

In directory 'articlee' create file .env(**do not forget to add it to .gitignore**) and add the following line:
```
    SECRET_KEY=<secret_key_you_generated>
```

Then you need to create MySQL database (using MySQL Workbench or any other tool), using SQL statement:
```SQL
    CREATE DATABASE articlee;
```