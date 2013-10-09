==========
Quickstart
==========

Installation
------------

Install MAdmin from pypi in a virtualenv::

    virtualenv madmin # To create a virtualenv
    source madmin/bin/activate # To active the virtualenv
    pip install madmin


Configuration
-------------

The configuration is located in ``$VIRTUAL_ENV/etc/madmin.cfg``.

To connect to a local mongodb, use the provided example config file::

    [mongodb]
    host = 127.0.0.1
    db = my_database
    replica_set = rs1  # optional, only specify if replication is active
    user = me  # optional, specify only if auth is active
    password = pssst  # optional, specify only if auth is active

    [rw.plugins]
    rw.db = True

Starting
--------

Start the application via::

    rw serv madmin

