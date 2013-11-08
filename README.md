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
   $ cp settings/local.py-dist settings/local.py
   ```

   The file is commented to explain what each setting does and how to customize
   them.

6. Initialize your database structure:

   ```sh
   $ python manage.py syncdb
   ```

[git]: http://git-scm.com/
[git-clone]: https://help.github.com/articles/fork-a-repo
[python]: http://www.python.org/
[mysql]: http://dev.mysql.com/doc/refman/5.6/en/installing.html


Running the Development Server
------------------------------
You can launch the development server like so:

```sh
$ python manage.py runserver
```


License
-------
This software is licensed under the `Mozilla Public License v. 2.0`_. For more
information, read the file ``LICENSE``.

.. _Mozilla Public License v. 2.0: http://mozilla.org/MPL/2.0/
