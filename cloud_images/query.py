# coding: utf-8
"""
Ubuntu Enterprise Cloud
cloud-images query interface

https://help.ubuntu.com/community/UEC/Images

"""

from __future__ import print_function
import urllib3

try:
    import boto.ec2
except ImportError:
    boto = None

# CI doc paths
CI_ROOT = 'https://cloud-images.ubuntu.com/query'
CI_QUERY_FORMAT = '{root}/{release_name}/{build_name}/{doc}{suffix}'
CI_DOC_DAILY = 'daily'
CI_DOC_RELEASED = 'released'
CI_DOC_IMAGE_DOWNLOAD = '-dl'
CI_DOC_CURRENT = '.current'
CI_DOC_SUFFIX = '.txt'

# Image build names
IMAGE_BUILD_SERVER = 'server'
IMAGE_BUILD_DESKTOP = 'desktop'

# CI doc fields
IMAGE_LABEL_RELEASE = 'release'
IMAGE_LABEL_DAILY = 'daily'
IMAGE_SERIAL_CURRENT = 'current'

# Virtualization Types
AMI_VM_STANDARD = 'paravirtual'
AMI_VM_HVM = 'hvm'
# Storage Backing Types
AMI_INSTANCE_STORE = 'instance-store'
AMI_EBS_STORE = 'ebs'
# Compile targets
CI_64_BIT = 'amd64'
AMI_64_BIT = 'x86_64'
AMI_32_BIT = 'i386'

# AWS validation constants
AWS_CANONICAL_ID = '099720109477'
AWS_IMAGE_STATE_AVAILABLE = 'available'
CI_ARCH_MAP = {
    AMI_32_BIT: AMI_32_BIT,
    CI_64_BIT: CI_64_BIT,
    AMI_64_BIT: CI_64_BIT
}

def lookup_ami(release_name, build_name=None, label=None, serial=None,
               filterkv=None):
    """
    Returns matching :class:`UbuntuAMI` objects, given query parameters:

    :param release_name: name of release (e.g.: lucid, precise)
    :type release_name: str
    :param build_name: `server` or `client` (default: `server`)
    :type build_name: str
    :param label: `release`, `daily`, or a specific release label (e.g.:
                  `alpha2`) (default: `release`)
    :type label: str
    :param serial: a locked serial version (default: `<current>`)
    :type serial: str
    :param filterkv: key-value pairs to filter results by boolean AND
                   (keys e.g.: `arch`, `root_store`, `region`)
    :type filterkv: dict

    :returns: :class:`UbuntuImageList` containing class:`UbuntuAMI` instances
    :raises: :class:`ImageNotFound`

    """

    return _lookup(
        release_name, build_name=build_name, label=label, serial=serial,
        image_class=UbuntuAMI, filterkv=filterkv)


def lookup_image(release_name, build_name=None, label=None, serial=None,
                 filterkv=None):
    """
    Returns a matching :class:`UbuntuImage` objects, given query parameters:

    :param release_name: name of release (e.g.: lucid, precise)
    :type release_name: str
    :param build_name: `server` or `client` (default: `server`)
    :type build_name: str
    :param label: `release`, `daily`, or a specific release label (e.g.:
                  `alpha2`) (default: `release`)
    :type label: str
    :param serial: a locked serial version (default: `<current>`)
    :type serial: str
    :param kwargs: key-value pairs to filter results by, (e.g.: `arch`)
    :type kwargs: dict

    :returns: :class:`UbuntuImageList` containing :class:`UbuntuImage` instances
    :raises: :class:`ImageNotFound`

    """

    return _lookup(
        release_name, build_name=build_name, label=label, serial=serial,
        is_image_dl=True, image_class=UbuntuAMI, filterkv=filterkv)


def _lookup(release_name, image_class, build_name=None, label=None, serial=None,
            is_image_dl=False, filterkv=None):
    if not build_name: build_name = IMAGE_BUILD_SERVER
    if not label: label = IMAGE_LABEL_RELEASE
    if not serial: serial = IMAGE_SERIAL_CURRENT

    is_release = label == IMAGE_LABEL_RELEASE
    is_daily = label == IMAGE_LABEL_DAILY
    is_current = serial == IMAGE_SERIAL_CURRENT

    url = _build_url(
        release_name, build_name, is_daily=is_daily, is_release=is_release,
        is_current=is_current, is_image_dl=is_image_dl)

    imgs = UbuntuImageList(url=url, image_class=image_class)

    if filterkv:
        return imgs.filter(**filterkv)

    return imgs

def _build_url(release_name, build_name, is_daily, is_release, is_current,
               is_image_dl=False, root=CI_ROOT):
    """ Builds a Ubuntu Cloud Image Query url """
    if is_release:
        doc = CI_DOC_RELEASED
    elif is_daily:
        doc = CI_DOC_DAILY

    if is_image_dl:
        doc += CI_DOC_IMAGE_DOWNLOAD
    if is_current:
        doc += CI_DOC_CURRENT

    url = CI_QUERY_FORMAT.format(**
        {'root': root,
         'release_name': release_name,
         'build_name': build_name,
         'doc': doc,
         'suffix': CI_DOC_SUFFIX
         })

    return url

class ImageValidationError(Exception):
    def __init__(self, ubuntu_image, aws_image, reason):
        """
        Exception raised when ubuntu_image does not pass

        :func:`UbuntuAMI.validate`
        :param ubuntu_image:
        :type ubuntu_image: :class:`UbuntuAMI`
        :param aws_image:
        :type aws_image: :class:`

        """
        self.ubuntu_image = ubuntu_image
        self.aws_image = aws_image
        self.reason = reason

    def __unicode__(self):
        return '{}: {}'.format(self.__class__.__name__, self.reason)


class UbuntuImage(object):
    #: overridden by children
    field_order = tuple()
    base_field_order = ('release_name', 'build_name', 'label', 'serial')
    def __init__(self, release_name=None, build_name=None, label=None,
                 serial=None, arch=None):
        #: known as `suite` in UEC docs
        self.release_name = release_name
        self.build_name = build_name
        self.label = label
        self.serial = serial
        self.arch = arch

    def _head_str(self):
        return 'release_name\tbuild_name\tlabel\tserial\tarch'

    def _line_str(self):
        return '{}\t{}\t{}\t{}\t{}'.format(
            self.release_name, self.build_name, self.label, self.serial,
            self.arch)

    @classmethod
    def parse_query_line(cls, line):
        fields = line.split('\t')
        return dict(zip(cls.field_order, fields))

    @classmethod
    def instantiate_from_query_line(cls, line):
        return cls(**cls.parse_query_line(line))


class UbuntuAMI(UbuntuImage):
    field_order = UbuntuImage.base_field_order + (
        'root_store', 'arch', 'region', 'ami', 'aki', 'ari', 'vm_type')

    def __init__(self, root_store=None, region=None, ami=None, aki=None,
                 ari=None, vm_type=None, **kwargs):
        super(UbuntuAMI, self).__init__(**kwargs)
        self.root_store = root_store
        self.region = region
        self.ami = ami
        self.aki = aki
        self.ari = ari
        self.vm_type = vm_type

    def _head_str(self):
        head_part = '\tregion\troot_store\tami\taki\tari\tvm_type'
        return super(UbuntuAMI, self)._head_str() + head_part

    def _line_str(self):
        line_part = '\t{}\t{}\t{}\t{}\t{}\t{}'.format(
            self.region, self.root_store, self.ami, self.aki, self.ari,
            self.vm_type)
        return super(UbuntuAMI, self)._line_str() + line_part

    def validate(self):
        """
        Validates a :class:`UbuntuAMI` against :class:`boto.ec2.image.Image`
        to confirm the assumptions about the image description are correct.
        Read: paranoia.

        Requires the usual `boto` credentials to be available. See `boto`
        docs for more information on that.

        :raises: `ImportError` when :mod:`boto` is not found.

        Validates this instance against image definition with AWS via boto:
        :class:`boto.ec2.Image`

        """
        if not boto:
            raise ImportError('boto required for AMI image validation')

        conn = boto.ec2.connect_to_region(self.region)
        image = conn.get_image(self.ami)

        if self.root_store != image.root_device_type:
            raise ImageValidationError(self, image, 'root_device_type mismatch')

        if self.vm_type != image.virtualization_type:
            raise ImageValidationError(
                self, image, 'virtualization_type mismatch')

        if self.arch != CI_ARCH_MAP[image.architecture]:
            raise ImageValidationError(self, image, 'architecture mismatch')

        if image.state != AWS_IMAGE_STATE_AVAILABLE:
            raise ImageValidationError(self, image, 'image state unavailable')

        if image.owner_id != AWS_CANONICAL_ID:
            raise ImageValidationError(
                self, image, 'owner_id not AWS_CANONICAL_ID')

        return True


class UbuntuImageDownload(UbuntuImage):
    field_order = UbuntuImage.base_field_order + (
        'arch', 'download_path', 'suggested_name')

    def __init__(self, download_path=None, suggested_name=None, **kwargs):
        super(UbuntuImageDownload, self).__init__(**kwargs)
        self.download_path = download_path
        self.suggested_name = suggested_name

    def _head_str(self):
        head_part = '\tdownload_path\tsuggested_name'
        return super(UbuntuImageDownload, self)._head_str() + head_part

    def _line_str(self):
        line_part = '\t{}\t{}'.format(self.download_path, self.suggested_name)
        return super(UbuntuImageDownload, self)._line_str() + line_part


class UbuntuImageList(object):
    def __init__(self, images=None, url=None, image_class=None):
        self._images = images
        self.url = url
        self.image_class = image_class
        self._response = None

    def __len__(self):
        return len(self.images)

    def __iter__(self):
        return iter(self.images)

    def __getitem__(self, idx):
        return self.images[idx]

    def print_list(self):
        if self.images:
            print(self.images[0]._head_str())
            for image in self.images:
                print(image._line_str())

    @property
    def images(self):
        if self._images is None:
            self._images = map(
                lambda line: self.image_class.instantiate_from_query_line(line),
                self.response)
        return self._images

    @property
    def response(self):
        if not self._response:
            # TODO: implement caching layer
            headers = urllib3.make_headers(accept_encoding=True)
            http = urllib3.PoolManager()
            self._response = http.request('GET', self.url, headers=headers)
            for line in self._response.data.split('\n'):
                line = line.strip()
                if line:
                    yield line

    def all(self):
        return UbuntuImageList(images=self.images)

    def filter(self, **kwargs):
        # fix arch if specified for amd64/x86_64 issue
        if 'arch' in kwargs and kwargs['arch']:
            kwargs['arch'] = CI_ARCH_MAP[kwargs['arch']]

        return UbuntuImageList(images=filter(
            lambda inst: all([getattr(inst, k) == v for k,v in kwargs.items()]),
            self.images))
