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

If you are using pipenv, clone this repository and run in the command line:
```
    pipenv install
```

To activate environment using pipenv, run in the command line:
```
    pipenv shell
```

In 'articlee.settings.py' add the following imports:
```python
    import os
    from pathlib import Path
    from django.contrib.messages import constants as messages
    from django.urls import reverse_lazy
    import environ
```