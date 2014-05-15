oneanddone
==========

The "One and Done" initiative, previously known as "QA Taskboard", is a workflow
where Mozilla community contributors can pick tasks and work on them - one at a
time, one day at a time - and feel good about doing them.

One and Done is written with [Playdoh][playdoh] and [Django][django].

If you're interested in helping us out, please read through
[the blog post][blogpost] and reach out to us!

[django]: http://www.djangoproject.com/
[playdoh]: https://github.com/mozilla/playdoh
[blogpost]: https://quality.mozilla.org/2013/10/qa-taskboard-development-call-for-participation/


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

3. Install the compiled requirements:

   ```sh
   $ pip install -r requirements/compiled.txt
   ```

4. Set up a local MySQL database. The [MySQL Installation Documentation][mysql]
   explains how to do this. Make sure your DB is utf8.

5. Configure your local settings by copying `oneanddone/settings/local.py-dist` to
   `oneanddone/settings/local.py` and customizing the settings in it:

   ```sh
   $ cp oneanddone/settings/local.py-dist oneanddone/settings/local.py
   ```

   The file is commented to explain what each setting does and how to customize
   them. One item in the local.py settings file you are going to want to change, if
   you are running this locally and not over HTTPS, is the following.

   Open up local.py, find and uncomment SESSION_COOKIE_SECURE = False


7. Create the initial empty database:

   ```sh
   # Start the MySQL server
   $ mysql.server start
   # Once successfully started, log into the console
   # using your username and password
   $ mysql -uroot -p
   # Create the database
   mysql> create database oneanddone;
   ```

8. Initialize your database structure:

   ```sh
   $ python manage.py syncdb
   ```

Applying Migrations
-------------------

We're using [South][south] to handle database migrations. To apply the migrations,
run the following:

   ```sh
   $ ./manage.py migrate oneanddone.tasks && ./manage.py migrate oneanddone.users
   ```

If you make changes to an existing model you will need to regeneratre the schema migration as follows:

   ```sh
   $ ./manage.py schemamigration oneanddone.tasks --auto
   ```

To generate a blank schema migration:

   ```sh
   $ ./manage.py datamigration oneanddone.mymodel data_migration_name
   ```

Then fill in the generated file with logic, fixtures, etc. You can then apply this migration as above with:

   ```sh
   $ ./manage.py migrate oneanddone.mymodel
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

If you are asked to create a super user, just enter no and let the process complete.


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
