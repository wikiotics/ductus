Testing Ductus
==============


Ductus uses unit tests to make sure everything is running as expected.
If you contribute code, we strongly encourage you to cover your code with tests.

Ductus relies on 2 different backends to run tests:
    - pytest for the backend
    - the Django built-in LiveServerTestCase (that uses Selenium) for front end testing


Backend testing
---------------

Backend tests rely on pytest.

Assuming you've setup ductus following the docs in :ref:`install`,
you can run them with::

    ./ductusenv/bin/python ./runtests.py

you may need to prepend ``PYTHON_PATH=/path/to/ductus_local_settings.py`` if you want those settings taken into account.

pytest files are located under ``<ductus_root>/tests``.

To create more tests, either extend one the of the existing files in there, or create a new one, making sure you call it ``test_*.py`` (or pytest won't do anything with it).


Frontend testing (javascript)
-----------------------------

It uses the Django built-in LiveServerTestCase_ so that we can use Selenium to test javascript.

You run those tests with::

    ./ductusenv/bin/python manage.py test ductus

You can also run specific tests by issuing::

    ./ductusenv/bin/python manage.py test ductus.TestClassName

or a single one with::

    ./ductusenv/bin/python manage.py test ductus.TestClassName.test_function_name

(as above, you may need to amend your path so that your local settings are included.)

Adding tests
''''''''''''

Test files are located under ``<ductus_root>/ductus/tests``. If you create additional files, make sure they are NOT called ``test_*.py`` as they may interfere with pytest (and most likely fail there).

To add a test to an existing file, simply create a new function in the existing class, following existing examples.

To add tests in a new file (to cover some new area of the code, like a new module):

 * create a new file for your test code named after the module it is meant to test (and using a similar path under ``ductus/tests/``)
 * make sure each new directory contains an empty ``__init__.py`` file
 * add an import statement for your file in ``ductus/tests/__ini__.py``

.. _LiveServerTestCase: https://docs.djangoproject.com/en/dev/topics/testing/#live-test-server

Note: if you know how to unify pytest and Django's Selenium testing, please be in touch :)
