import os
import tempfile

import ocfl
from settings import REPO


class MigrationError(RuntimeError):
    pass


def _get_fedora3_datastreams(src_dir, pid):
    #need to get list of datastreams to migrate
    #   could use fedora_object.ds_list - any deleted datastreams would just be in old versions of the ocfl object
    #   how to handle the history of fedora objects?
    #       could just have two versions: 1 that contains all datastreams (whether deleted or not), 2nd that removes the deleted datastreams
    #           this doesn't handle objects that have 3+ versions of a datastream
    #       create a version that has all datastreams, whether deleted or not
    #           as long as needed: create another version, that updates any datastreams that have a new state or new content
    #       note: Fedora needs to still return the content for deleted datastreams (instead of a 404).
    fedora_object = REPO.get_object(pid)
    for ds_name in fedora_object.ds_list.keys():
        print(f'  {ds_name}')
        ds_obj = fedora_object.getDatastreamObject(ds_name)
        if ds_obj.state == 'A':
            with open(os.path.join(src_dir, ds_name), 'wb') as f:
                for chunk in ds_obj.get_chunked_content():
                    f.write(chunk)


def migrate(pid, storage_root):
    obj_root = os.path.join(storage_root, pid)
    if os.path.exists(obj_root):
        raise MigrationError(f'{obj_root} already exists')
    ocfl_obj = ocfl.Object(identifier=pid)
    version_metadata = ocfl.version.VersionMetadata()
    with tempfile.TemporaryDirectory() as src_dir:
        _get_fedora3_datastreams(src_dir, pid)
        ocfl_obj.create(srcdir=src_dir, metadata=version_metadata, objdir=obj_root)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Migrate Fedora3 repository to OCFL storage root')
    parser.add_argument('pid')
    args = parser.parse_args()
    migrate(args.pid)

