############
Contributing
############

This document provides guidelines for people who want to contribute to the
`MLV-tools` project.


**************
Create tickets
**************

Please use bugtracker **before** starting some work:

* check if the bug or feature request has already been filed. It may have been
  answered too!

* else create a new ticket.

* if you plan to contribute, tell us, so that we are given an opportunity to
  give feedback as soon as possible.

* Then, in your commit messages, reference the ticket with some
  ``Refs #TICKET-ID`` syntax.


******************
Use topic branches
******************

* Work in branches.

* Prefix your branch with the ticket ID corresponding to the issue. As an
  example, if you are working on ticket #23 which is about contribute
  documentation, name your branch like ``23-contribute-doc``.

* If you work in a development branch and want to refresh it with changes from
  master, please [rebase](http://git-scm.com/book/en/Git-Branching-Rebasing) or 
  [merge-based rebase](https://tech.people-doc.com/psycho-rebasing.html), i.e. do not merge master.


***********
Fork, clone
***********

Clone `ml-versioning-tools` repository (adapt to use your own fork):


    git clone https://github.com/peopledoc/ml-versioning-tools.git
    cd ml-versioning-tools/


*************
Usual actions
*************

The `Makefile` is the reference card for usual actions in development
environment:

* Install development toolkit with [pip](https://pypi.org/project/pip/): ``make develop``.

* Run tests: ``make test``.

* Cleanup local repository: ``make clean``

See also ``make help``.


.. rubric:: Notes & references

.. target-notes::

.. _`rebase`: http://git-scm.com/book/en/Git-Branching-Rebasing
.. _`merge-based rebase`: https://tech.people-doc.com/psycho-rebasing.html
.. _`pip`: https://pypi.org/project/pip/
.. _`tox`: https://pypi.org/project/tox/
.. _`Sphinx`: https://pypi.org/project/Sphinx/
.. _`zest.releaser`: https://pypi.org/project/zest.releaser/
