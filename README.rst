cloud_images README
===================

.. contents:: Table of Contents

Introduction
------------

cloud_images queries the index of Canonical-provided Ubuntu images that are
part of `Ubuntu Cloud Guest <https://help.ubuntu.com/community/UEC/Images>`_
program and available at `Ubuntu Cloud Images
<http://cloud-images.ubuntu.com>`_.

This is useful for programatic launching of AMIs as well as a quick reference
for developers and ops.

Command Line Interface
----------------------

The `cloud_images` script provided accepts keyword arguments to return a
tab-separated list of matching images.

With `boto` and appropriate boto-AWS-authentication set up, the `--validate`
argument will validate the existence of a Ubuntu-provided AMI with AWS.

API
---

`cloud_images.query` includes methods and classes to enable programatic access
to the Ubuntu Cloud Images index.

TODO
----

#) Improve documentation
#) Implement query caching
