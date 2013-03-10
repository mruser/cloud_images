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

::

  usage: cloud_images [-h] [--build_name BUILD_NAME] [--serial SERIAL]
                      [--label LABEL] [--image-download] [--validate]
                      [--arch ARCH] [--region REGION] [--vm_type VM_TYPE]
                      [--root_store ROOT_STORE]
                      release_name

  positional arguments:
    release_name          name of release (e.g.: lucid, precise)
 
  optional arguments:
    -h, --help            show this help message and exit
    --build_name BUILD_NAME
                          `server` or `client` (default: `server`)
    --serial SERIAL       a locked serial version (default: <current>)
    --label LABEL         `release`, `daily`, or a specific release label
                          (e.g.:`alpha2`) (default: `release`)
    --image-download      returns an image download reference instead of an AMI
    --validate            Validates an AMI using boto and environment AWS
                          credentials
    --arch ARCH           Adds `arch` filter to result set
    --region REGION       Adds `region` filter to result set
    --vm_type VM_TYPE     Adds `vm_type` filter to result set
    --root_store ROOT_STORE
                          Adds `root_store` filter to result set

API
---

`cloud_images.query` includes methods and classes to enable programatic access
to the Ubuntu Cloud Images index.

TODO
----

#) Improve documentation
#) Implement query caching
