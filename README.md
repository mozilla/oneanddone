oneanddone
==========

One and Done is written with [Django][django].

If you're interested in helping us out, please read through the
[project wiki][wiki] and reach out to us!

About the project:
>Contribute to Mozilla - One task at a time, One day at a time.
>
>One and Done gives users a wide variety of ways to contribute to Mozilla. 
>You can pick an easy task that only takes a few minutes - or take on a 
>bigger challenge. This includes working on manual testing, automation, bug 
>verification, mobile testing and more. Tasks are from a variety of Mozilla teams - so you 
>can get involved with Automation, Firefox OS, Desktop Firefox, Mozilla 
>websites, Services, Thunderbird and more.

[django]: http://www.djangoproject.com/
[wiki]: https://wiki.mozilla.org/QA/OneandDone
[persona]: https://developer.mozilla.org/Persona/The_implementor_s_guide/Testing
[django-browserid]: https://github.com/mozilla/django-browserid


Development Setup
-----------------
These instructions assume you have [git][], [python][], and `pip` installed. If
you don't have `pip` installed, you can install it with `easy_install pip`.


1. Start by getting the source:

   ```sh
   $ git clone git@github.com:mozilla/oneanddone.git
   $ cd oneanddone
   ```
   Note you may want to fork and clone the repo as described in the
   [github docs][git-clone] if you are doing active development.

2. Create a virtualenv for One and Done. Skip the first step if you already have
   `virtualenv` installed.

   ```sh
   $ pip install virtualenv
   $ virtualenv venv
   $ source venv/bin/activate
   ```

3. Set up PostgreSQL locally. The [PostgreSQL Installation Documentation][postgres] explains how to do this.
   

4. Create the initial empty database; make sure it's utf8:
   ``` 
   # Log into the postgres console
   # using your username and password
   $ psql -U your_username
   ```
   In the mysql console:
   ```mysql
   CREATE DATABASE oneanddone;
   \q
   ```
   To run all parts of the application, you will eventually need to populate this empty database with some example data, especially Tasks. There are many ways to populate the database. The method you choose may depend on the kind of data you want to add.
      * Use the create/edit features of your local One and Done instance. For example sign in with an administrator account and go to the `/tasks/create/` URL of the app to create Tasks.
      * Use the Django admin section of your local One and Done instance by going to the `/admin` URL -- this also relies on an admin account. You can define Task Teams here, for example.
      * Use an external tool like PgAdmin.
      * Ask another active developer for a dump of their local database.

5. Install the requirements:
   ```sh
   $ ./bin/peep.py install -r requirements/requirements.txt
   ```
   _Note_: On OS X (in particular 10.8.5, Xcode 5.1), you may encounter the following error: `clang: error: unknown argument. '-mno-fused-madd'`. Try running peep with the `ARCHFLAGS` environment variable set, as follows: `ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future ./bin/peep.py install -r requirements/requirements.txt` 

6. Establish your local settings by copying `oneanddone/settings/local.py-dist` to
   `oneanddone/settings/local.py`:

   ```sh
   $ cp oneanddone/settings/local.py-dist oneanddone/settings/local.py
   ```
   
   The default settings in this file should work fine for a local dev environment, but the file
   is commented to describe how it can be customized. For example, if you wish to use `memcached` for caching instead of local memory, 
   you can change the `CACHES` section to read:
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
           'LOCATION': '127.0.0.1:11211',
           'TIMEOUT': 600,
       }
   }
   ```
   
7. Establish your local environment by copying `.env-dist` to `.env`:
   ```sh
   $ cp .env-dist .env
   ```

   As above, the default settings in this file should work fine for a local dev environment.

8. Initialize your database structure:
   ```sh
   $ python manage.py migrate
   ```

   Once finished, the `migrate` command should produce a message about which models have been migrated, similar to that shown below.

   ```
   Operations to perform:
     Synchronize unmigrated apps: authtoken, rest_framework, cookies, base, session_csrf
     Apply all migrations: tasks, users, sessions, admin, auth, contenttypes
   Synchronizing apps without migrations:
     Creating tables...
       Creating table authtoken_token
     Installing custom SQL...
     Installing indexes...
   Running migrations:
     Applying contenttypes.0001_initial... OK
     Applying auth.0001_initial... OK
     Applying admin.0001_initial... OK
     Applying sessions.0001_initial... OK
     Applying tasks.0001_initial... OK
     Applying users.0001_initial... OK
   ```

Users
-----

One and Done uses [BrowserID][django-browserid], a.k.a. Mozilla Persona, for user authentication. To add users to your local database, simply sign into your local One and Done instance. You may want to use dummy email accounts as described in Mozilla's guide to [testing Persona][persona].

You need at least one superuser to be able to develop and test administrative features of the project. You can create as many superusers as you like with `python manage.py createsuperuser`. After that, sign into your local One and Done instance with the superuser's email address as usual. 


Applying Migrations
-------------------

We're using built in [Django][django] database migrations. To apply the migrations,
run the following:

   ```sh
   $ ./manage.py migrate
   ```

If you make changes to an existing model, say `oneanddone.tasks`, you will need to regenerate the schema migration as follows:

   ```sh
   $ ./manage.py makemigrations tasks
   ```

To generate a blank data migration:

   ```sh
   # ./manage.py makemigrations --empty [model] [data_migration_name]
   # Example:
   $ ./manage.py makemigrations oneanddone.tasks task_data 
   ```

Then fill in the generated file with logic, fixtures, etc. You can then apply this migration as above with:

   ```sh
   $ ./manage.py migrate oneanddone.tasks
   ```


[git]: http://git-scm.com/
[git-clone]: https://help.github.com/articles/fork-a-repo
[python]: http://www.python.org/
[postgres]: http://www.postgresql.org/docs/
[south]: http://south.aeracode.org/


Running the Development Server
------------------------------
You can launch the development server like so:

```sh
$ python manage.py runserver
```

Running Unit Tests
------------------
You can run all the unit tests in verbose mode as follows:

```sh
$ python manage.py test -v 2
```
You can also run specific tests:
```sh
# All tests in tasks/tests/test_helpers module.
$ python manage.py test oneanddone.tasks.tests.test_helpers -v 2
# Just one test (PageUrlTests.test_basic)
$ python manage.py test oneanddone.tasks.tests.test_helpers:PageUrlTests.test_basic -v 2

```

REST API Support
----------------
There is a REST API support which enables:

* Getting complete list of Tasks.
* Getting details about a Task with a particular id.
* Create and Delete Tasks with a particular id.
The Task queries can be made by appending `api/v1/task/` to the base url.

GET and DELETE queries example.
```sh
curl -X GET http://127.0.0.1:8000/api/v1/task/ -H 'Authorization: Token d81e33c57b2d9471f4d6849bab3cb233b3b30468'
curl -X GET http://127.0.0.1:8000/api/v1/task/1/ -H 'Authorization: Token d81e33c57b2d9471f4d6849bab3cb233b3b30468'
curl -X DELETE http://127.0.0.1:8000/api/v1/task/1/ -H 'Authorization: Token d81e33c57b2d9471f4d6849bab3cb233b3b30468'
```

* Getting a complete list of Users.
* Getting details about a User with a particular email.
* Create and Delete Users with a particular email.
The User queries can be made by appending `api/v1/user/` to the base url.

GET and DELETE queries example.
```sh
curl -X GET http://127.0.0.1:8000/api/v1/user/ -H 'Authorization: Token d81e33c57b2d9471f4d6849bab3cb233b3b30468'
curl -X GET http://127.0.0.1:8000/api/v1/user/testuser@tesmail.com/ -H 'Authorization: Token d81e33c57b2d9471f4d6849bab3cb233b3b30468'
curl -X DELETE http://127.0.0.1:8000/api/v1/user/testuser@testmail.com/ -H 'Authorization: Token d81e33c57b2d9471f4d6849bab3cb233b3b30468'
```

#### The API uses a Token Authentication system.

Token used in examples above is just a sample and actual Tokens can be generated from the admin panel by going to `Authtoken > Tokens`.


Functional Tests
-----------------
Functional (Selenium) tests for oneanddone are maintained by the Web QA team and can be found at [oneanddone-tests].

[oneanddone-tests]: https://github.com/mozilla/oneanddone-tests


License
-------
This software is licensed under the [Mozilla Public License v. 2.0](http://mozilla.org/MPL/2.0/). For more
information, read the file ``LICENSE``.
