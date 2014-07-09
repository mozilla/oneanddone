oneanddone
==========

One and Done is written with [Playdoh][playdoh] and [Django][django].

If you're interested in helping us out, please read through the
[project wiki][wiki] and reach out to us!

About the project:
>Contribute to Mozilla QA - One task at a time, One day at a time.
>
>One and Done gives users a wide variety of ways to contribute to Mozilla. 
>You can pick an easy task that only takes a few minutes - or take on a 
>bigger challenge. This includes working on manual testing, automation, bug 
>verification, mobile testing and more. Tasks are from all QA teams - so you 
>can get involved with Automation, Firefox OS, Desktop Firefox, Mozilla 
>websites, Services, or Thunderbird.

[django]: http://www.djangoproject.com/
[playdoh]: https://github.com/mozilla/playdoh
[wiki]: https://wiki.mozilla.org/QA/OneandDone
[persona]: https://developer.mozilla.org/Persona/The_implementor_s_guide/Testing
[django-browserid]: https://github.com/mozilla/django-browserid


Development Setup
-----------------
These instructions assume you have [git][], [python][], and `pip` installed. If
you don't have `pip` installed, you can install it with `easy_install pip`.


1. Start by getting the source:

   ```sh
   $ git clone --recursive git@github.com:mozilla/oneanddone.git
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

3. Set up MySQL locally. The [MySQL Installation Documentation][mysql] explains how to do this.
   

4. Create the initial empty database; make sure it's utf8:
   ``` 
   # Start the MySQL server
   $ mysql.server start
   # Once successfully started, log into the console
   # using your username and password
   $ mysql -uroot -p
   ```
   In the mysql console:
   ```mysql
   CREATE DATABASE oneanddone 
   DEFAULT CHARACTER SET utf8 
   DEFAULT COLLATE utf8_general_ci;
   ```
   To run all parts of the application, you will eventually need to populate this empty database with some example data, especially Tasks. There are many ways to populate the database. The method you choose may depend on the kind of data you want to add.
      * Use the create/edit features of your local One and Done instance. For example sign in with an administrator account and go to the `/tasks/create/` URL of the app to create Tasks.
      
      * Use the Django admin section of your local One and Done instance by going to the `/admin` URL -- this also relies on an admin account. You can define Task Teams here, for example.
      
      * Use an external tool like MySQL Workbench.
      
      * Ask another active developer for a mysqldump of their local database.

5. Install the compiled and development requirements:

   ```sh
   $ pip install -r requirements/compiled.txt
   $ pip install -r requirements/dev.txt
   ```

6. Deploy the project in "development" mode:

   ```sh
   $ python setup.py develop
   ```


7. Configure your local settings by copying `oneanddone/settings/local.py-dist` to
   `oneanddone/settings/local.py` and customizing the settings in it:

   ```sh
   $ cp oneanddone/settings/local.py-dist oneanddone/settings/local.py
   ```

   The file is commented to explain what each setting does and how to customize
   them. One item in the local.py settings file you are going to want to change, if
   you are running this locally and not over HTTPS, is the following.

   Open up local.py, find and uncomment SESSION_COOKIE_SECURE = False


8. Initialize your database structure:

   ```sh
   $ python manage.py syncdb
   ```

If you are asked to create a superuser, do so. Don't worry if you miss this step: see the [Users](#users) section below for more information.

Once finished, the `syncdb` command should produce a message about which models have been synced. At the bottom, the message will include something like this:

   ```
   Not synced (use migrations):
    - oneanddone.tasks
    - oneanddone.users
    - rest_framework.authtoken
   ```

This means that you must also run `./manage.py migrate [model]` for each model that is not synced with `syncdb`. More information about South migrations is included under the [Applying Migrations](#applying-migrations) section below.

Users
-----

Playdoh uses [BrowserID][django-browserid], a.k.a. Mozilla Persona, for user authentication. To add users to your local database, simply sign into your local One and Done instance. You may want to use dummy email accounts as described in Mozilla's guide to [testing Persona][persona].

You need at least one superuser to be able to develop and test administrative features of the project. You can create as many superusers as you like with `python manage.py createsuperuser`. After that, sign into your local One and Done instance with the superuser's email address as usual. 


Applying Migrations
-------------------

We're using [South][south] to handle database migrations. To apply the migrations,
run the following:

   ```sh
   $ ./manage.py migrate oneanddone.tasks && ./manage.py migrate oneanddone.users
   ```

If you make changes to an existing model, say `oneanddone.tasks`, you will need to regeneratre the schema migration as follows:

   ```sh
   $ ./manage.py schemamigration oneanddone.tasks --auto
   ```

To generate a blank data migration:

   ```sh
   # ./manage.py datamigration [model] [data_migration_name]
   # Example:
   $ ./manage.py datamigration oneanddone.tasks task_data 
   ```

Then fill in the generated file with logic, fixtures, etc. You can then apply this migration as above with:

   ```sh
   $ ./manage.py migrate oneanddone.tasks
   ```


[git]: http://git-scm.com/
[git-clone]: https://help.github.com/articles/fork-a-repo
[python]: http://www.python.org/
[mysql]: http://dev.mysql.com/doc/refman/5.6/en/installing.html
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
You can also run spefic tests:
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
* Getting detail about a Task with particular id.
* Create and Delete Tasks with particular id.
The Task queries can be made by appending `api/v1/task/` to the base url.

GET and DELETE queries example.
```sh
curl -X GET http://127.0.0.1:8000/api/v1/task/ -H 'Authorization: Token d81e33c57b2d9471f4d6849bab3cb233b3b30468'
curl -X GET http://127.0.0.1:8000/api/v1/task/1/ -H 'Authorization: Token d81e33c57b2d9471f4d6849bab3cb233b3b30468'
curl -X DELETE http://127.0.0.1:8000/api/v1/task/1/ -H 'Authorization: Token d81e33c57b2d9471f4d6849bab3cb233b3b30468'
```

* Getting complete list of Users.
* Getting details about a User with particular email.
* Create and Delete Users with with particular email.
The User queries can be made by appending `api/v1/user/` to the base url.

GET and DELETE queries example.
```sh
curl -X GET http://127.0.0.1:8000/api/v1/user/ -H 'Authorization: Token d81e33c57b2d9471f4d6849bab3cb233b3b30468'
curl -X GET http://127.0.0.1:8000/api/v1/user/testuser@tesmail.com/ -H 'Authorization: Token d81e33c57b2d9471f4d6849bab3cb233b3b30468'
curl -X DELETE http://127.0.0.1:8000/api/v1/user/testuser@testmail.com/ -H 'Authorization: Token d81e33c57b2d9471f4d6849bab3cb233b3b30468'
```

#### The API uses a Token Authentication system.

Token used in examples above is just a sample and actual Tokens can be generated from the admin pannel by going to `Authtoken > Tokens`.


Functional Tests
-----------------
Functional (Selenium) tests for oneanddone are maintained by the Web QA team and can be found at [oneanddone-tests].

[oneanddone-tests]: https://github.com/mozilla/oneanddone-tests


License
-------
This software is licensed under the `Mozilla Public License v. 2.0`_. For more
information, read the file ``LICENSE``.

.. _Mozilla Public License v. 2.0: http://mozilla.org/MPL/2.0/
