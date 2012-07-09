.. _install:

Ductus installation
===================

Setting up a Ductus Development Instance is a great way to get a feel for the code and make any changes you would like to make.  Best of all, the system has a way of automatically pulling content from wikiotics.org, so you can make changes to the site's user interface and see how they work using actual content.

If you really want, you can even make your server face the public world and allow anybody else to use your improved version of Ductus (but let us know if you intend to do this; eventually you will need to register for an API key -- see `ticket #48`_).

Keep in mind if you are distributing code (even Javascript code), anything that is a derivative work of Ductus must fall under GPLv3 or later.

.. _ticket #48: https://code.ductus.us/ticket/48

Install base dependencies
-------------------------

To get started, install:

 * Python 2.7.x
 * lxml
 * Python Imaging Library ("PIL")
 * virtualenv
 * pip

(`virtualenv` and `pip` are not strictly required, but they make the install go a lot smoother, and the instructions below assume that they are installed.)

On Debian or Ubuntu, the following command should install everything we need at this point::

$ sudo apt-get install python-virtualenv python-pip python-lxml python-imaging

Obtain the source code
----------------------

Clone the git repository with::

$ git clone git://gitorious.org/ductus/ductus.git


If you have no previous experience with python/Django, the code should not be under you webserver root. Put it anywhere in your home folder, for instance.

The remainder of the instructions will assume (for simplicity) that you are in the directory that contains the source code, so we now run::

$ cd ductus/

Install python required and optional dependencies
-------------------------------------------------

`virtualenv` allows us to set up a virtual python environment where we can install the specific versions of packages known to work with Ductus.  To set up the environment, run the command::

$ virtualenv --system-site-packages ductusenv

If this fails, saying ``virtualenv: error: no such option: --system-site-packages``, then you must be using a version of virtualenv older than 1.7.  There is nothing to fear: simply remove this flag and run `virtualenv ductusenv`, as including system site packages was the default behavior in versions before 1.7 anyway.

If you care enough to make `git-status` ignore the `ductusenv` directory, run::

$ echo ductusenv/ >> .git/info/exclude

Once the environment is set up, we can run a single `pip` command to install all packages Ductus depends on, as given in source:requirements.txt. ::

$ ductusenv/bin/pip install -r requirements.txt

This command can be run again at any later time, if the requirements change (or simply to make sure everything is still in sync).

Set up site-specific configuration
----------------------------------

Create a file called `ductus_local_settings.py` in your ``PYTHONPATH`` with the following contents::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/ductus_data_path/db',
        }
    }

    DUCTUS_MEDIA_PREFIX = "/static/"
    DUCTUS_DISKCACHE_DIR = '/ductus_data_path/ductus-diskcache'
    DUCTUS_WIKI_REMOTE = "http://wikiotics.org/"
    DUCTUS_MEDIACACHE_DIR = '/ductus_data_path/storage'

    SECRET_KEY = ""

`SECRET_KEY` should be filled in with a string of random characters -- the more the better (somewhere in the ballpark of 64 characters is good; this can be obtained by running ``pwgen -sy 64``).

Create a file `ductus_site.py` in your `PYTHONPATH` with the following contents::

    from ductus.resource.storage import LocalStorageBackend, UnionStorageBackend, RemoteDuctusStorageBackend
    local = LocalStorageBackend('/ductus_data_path/storage')
    remote = RemoteDuctusStorageBackend("http://wikiotics.org/")
    storage_backend = UnionStorageBackend([local, remote], collect_resources=True)

In both files, replace `ductus_data_path` with an appropriate pathname.  The code in `ductus_site.py` sets up a local storage backend, chained to a remote storage backend.  If a resource is not found in the local database, it will query wikiotics.org to see if it is available there (and then cache it indefinitely).

Create database
---------------

The database is synced using the standard Django command::

$ ./ductusenv/bin/python manage.py syncdb

Set up and run a development server
-----------------------------------

Django (the framework behind ductus) ships with a development webserver so you don't need to tinker with your server config for testing::

$ ./ductusenv/bin/python manage.py runserver

This will run the Django development server on port 8000 by default. To change that port to, say, 8080, run instead::

$ ./ductusenv/bin/python manage.py runserver 8080

Assuming the above command returns no error messages, you can now point your browser to http://localhost:8000/ and see your local Ductus instance.

Develop Ductus
--------------

Improve code.  Submit patches.  Read the :ref:`overview`.  If your goal is to get patches accepted, bring up any major changes on the discussion list first.  Read the git documentation to understand how to rebase your changes onto the most recent development version of Ductus in the future.  If you haven't made any changes to your local version of Ductus, a regular "git pull" will suffice to update your repository and checkout.
