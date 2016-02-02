Tests for oneanddone.mozilla.org
================================

This folder contains Selenium tests used to test the One and Done web site.

[![license](https://img.shields.io/badge/license-MPL%202.0-blue.svg)](https://github.com/mozilla/oneanddone/blob/master/LICENSE)
[![travis](https://img.shields.io/travis/mozilla/oneanddone.svg?label=travis)](http://travis-ci.org/mozilla/oneanddone/)
[![dev](https://img.shields.io/jenkins/s/https/webqa-ci.mozilla.com/oneanddone.dev.svg?label=dev)](https://webqa-ci.mozilla.com/job/oneanddone.dev/)
[![stage](https://img.shields.io/jenkins/s/https/webqa-ci.mozilla.com/oneanddone.stage.svg?label=stage)](https://webqa-ci.mozilla.com/job/oneanddone.stage/)

Getting involved
----------------

We love working with contributors to fill out the Selenium test coverage for One and Done,
but it does require a few skills.
By contributing to our test suite you will have an opportunity to learn and/or improve your
skills with Python, Selenium WebDriver, GitHub, Virtualenv, the Page Object Model, and more.

For some resources for learning about these technologies, take a look at our documentation on 
[Running Web QA automated tests][runningtests].

The following contributors have submitted pull requests to oneanddone:

https://github.com/mozilla/oneanddone/contributors

Questions are always welcome
----------------------------
While we take pains to keep our documentation updated, the best source of information is those 
of us who work on the project.  
Don't be afraid to join us in irc.mozilla.org [#mozwebqa][mozwebqa] to ask questions about our 
Selenium tests.
We also have a [mailing list][mailing_list] available that you are welcome to join and post to.

How to run the tests locally
-----------------------------------------
We maintain a [detailed guide][runningtests] to running our automated tests which can be found on the MDN website.
If you want to get started quickly, you can try following the steps in our quick-start instructions below:

###Clone the repository
If you have cloned this project already then you can skip this, otherwise you'll need to clone this repo using Git.
If you do not know how to clone a GitHub repository, check out this 
[help page][cloninghelp] from GitHub.

If you think you would like to contribute to the tests by writing or maintaining them in the future,
it would be a good idea to create a fork of this repository first, and then clone that.
GitHub also has great instructions for [forking a repository][forkinghelp].

###Create or activate a Python virtual environment
You should install this project's dependencies (which is described in the next step) into a virtual environment
in order to avoid impacting the rest of your system, and to make problem solving easier.
If you already have a virtual environment for these tests, then you should activate it, 
otherwise you should create a new one.
For more information on working with virtual environments see our 
[our quickstart guide][virtualenvqs] and also [this blog post][virtualenvblogpost].

### Install dependencies
Install the Python packages that are needed to run our tests using pip. In a terminal, 
from the the project root, issue the following command:

```bash
$ pip install -Ur requirements/test.txt
```

### Run the tests

Tests are run using the command line. Below are a couple of examples of running the tests:

To run all of the tests against the development environment, 
pass in the correct value for --base-url, like so:

```bash
$ py.test --base-url https://oneanddone-dev.allizom.org --driver Firefox oneanddone/tests/functional/
```

You can also run the tests against a local instance of One and Done, if you have the project
properly configured. To do so, you must install the local test dependencies into
your virtualenv, like so:

```bash
$ pip install -Ur requirements/test-local.txt
```

To run the tests against a local instance the command line would be:

```bash
$ py.test --driver Firefox oneanddone/tests/functional/
```

The pytest plugin that we use for running tests has a number of advanced command-line 
options available. To see the options available, try running:

    py.test --help

The full documentation for the plugin can be found at the [pytest-selenium GitHub project page] [pytestselenium].

[runningtests]: https://developer.mozilla.org/en-US/docs/Mozilla/QA/Running_Web_QA_automated_tests
[mozwebqa]:http://widget01.mibbit.com/?settings=1b10107157e79b08f2bf99a11f521973&server=irc.mozilla.org&channel=%23mozwebqa
[mailing_list]:https://mail.mozilla.org/listinfo/mozwebqa
[cloninghelp]: https://help.github.com/articles/cloning-a-repository
[forkinghelp]: https://help.github.com/articles/fork-a-repo
[virtualenvqs]: https://wiki.mozilla.org/QA/Execution/Web_Testing/Automation/Virtual_Environments
[virtualenvblogpost]: http://www.silverwareconsulting.com/index.cfm/2012/7/24/Getting-Started-with-virtualenv-and-virtualenvwrapper-in-Python
[pytestselenium]: https://github.com/davehunt/pytest-selenium
