from __future__ import print_function
import sys
import argparse

from cloud_images.query import lookup_ami, lookup_image


def run():
    """
    Look up a desired ubuntu AMI or Image Download given query arguments.

    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'release_name',
        help='name of release (e.g.: lucid, precise)')
    parser.add_argument(
        '--build_name',
        default='server',
        help='`server` or `client` (default: `server`)')
    parser.add_argument(
        '--serial',
        help='a locked serial version (default: <current>)')
    parser.add_argument(
        '--label',
        help='`release`, `daily`, or a specific release label (e.g.:`alpha2`) '
             '(default: `release`)')
    parser.add_argument(
        '--image-download',
        action='store_true',
        default=False,
        help='returns an image download reference instead of an AMI')
    parser.add_argument(
        '--validate',
        action='store_true',
        default=False,
        help='Validates an AMI using boto and environment AWS credentials')

    # filter args
    filter_args = ('arch', 'region', 'vm_type', 'root_store')
    for arg in filter_args:
        parser.add_argument(
            '--{}'.format(arg),
            help='Adds `{}` filter to result set'.format(arg))

    args = parser.parse_args()

    if args.image_download:
        lookup_cmd = lookup_image
    else:
        lookup_cmd = lookup_ami

    images = lookup_cmd(
        args.release_name, build_name=args.build_name, label=args.label,
        serial=args.serial)

    if any([hasattr(args, arg) for arg in filter_args]):
        filterkv = {}
        for arg in filter_args:
            if getattr(args, arg):
                filterkv[arg] = getattr(args, arg)

        images = images.filter(**filterkv)

    if not len(images):
        print('No images found that match your criteria', file=sys.stderr)
        return False

    images.print_list()

    if args.validate:
        if len(images) > 1:
            print('Unable to validate: will only validate when narriowed to'
                  ' one result', file=sys.stderr)
            return False

        if images[0].validate():
            print('Validation successful')

