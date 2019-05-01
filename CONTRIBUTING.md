Contributing
============

This document provides guidelines for people who want to contribute to the
`MLV-tools` project.



Create tickets
--------------

Please use bugtracker **before** starting some work:

- Check if the bug or feature request has already been filed. It may have been
  answered too!

- Else create a new ticket.

- If you plan to contribute, tell us, so that we are given an opportunity to
  give feedback as soon as possible.

- Then, in your commit messages, reference the ticket with some
  `Refs #TICKET-ID` syntax.



Use feature branches
--------------------

- Work in branches.

- Prefix your branch with the ticket ID corresponding to the issue. As an
  example, if you are working on ticket #23 which is about contribute
  documentation, name your branch like `23-contribute_doc`.

- If you work in a development branch and want to refresh it with changes from
  master, please [rebase](http://git-scm.com/book/en/Git-Branching-Rebasing) or 
  [merge-based rebase](https://tech.people-doc.com/psycho-rebasing.html), i.e. do not merge master.


Tests
-----

There is 3 levels of tests:

- **unit and functional**: close to the code, they test function/module behavior (`make test`).
- **large**: run inside a docker container on the freshly packaged tool. Ensure packaging is well done
and it tests global scenario (`large-test-local`).

Each PR must contain at least unit tests and it can be merged only if the Continuous Integration is "green".

Usual actions
--------------

The `Makefile` is the reference card for usual actions in development
environment:

* Install development toolkit with [pip](https://pypi.org/project/pip/): `make develop`.

* Run tests: `make test`, `make large-test-local`.

* Check syntax: `make lint`

* Cleanup local repository: `make clean`

* Package local sources: `make package`

See also `make help`.
