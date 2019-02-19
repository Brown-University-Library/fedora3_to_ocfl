import os
import tempfile

from eulfedora.server import Repository
import ocfl
from settings import FEDORA_ROOT, FEDORA_USERNAME, FEDORA_PASSWORD


repo = Repository(root=FEDORA_ROOT, username=FEDORA_USERNAME, password=FEDORA_PASSWORD)


def _get_fedora3_datastreams(src_dir, pid):
    #need to get list of datastreams to migrate
    #   could use fedora_object.ds_list - any deleted datastreams would just be in old versions of the ocfl object
    #   how to handle the history of fedora objects?
    #       could just have two versions: 1 that contains all datastreams (whether deleted or not), 2nd that removes the deleted datastreams
    #           this doesn't handle objects that have 3+ versions of a datastream
    #       create a version that has all datastreams, whether deleted or not
    #           as long as needed: create another version, that updates any datastreams that have a new state or new content
    #       note: Fedora needs to still return the content for deleted datastreams (instead of a 404).
    fedora_object = repo.get_object(pid)
    for ds_name in fedora_object.ds_list.keys():
        print(f'  {ds_name}')
        ds_obj = fedora_object.getDatastreamObject(ds_name)
        if ds_obj.state == 'A':
            with open(os.path.join(src_dir, ds_name), 'wb') as f:
                for chunk in ds_obj.get_chunked_content():
                    f.write(chunk)


def migrate(args):
    pid = args.pid
    ocfl_obj = ocfl.Object(identifier=args.pid)
    version_metadata = ocfl.version.VersionMetadata()
    with tempfile.TemporaryDirectory() as src_dir:
        _get_fedora3_datastreams(src_dir, args.pid)
        with tempfile.TemporaryDirectory() as tmp_dir:
            obj_root = os.path.join(tmp_dir, args.pid)
            ocfl_obj.create(srcdir=src_dir, metadata=version_metadata, objdir=obj_root)
            print(os.listdir(tmp_dir))
            print(os.listdir(obj_root))
            print(os.listdir(os.path.join(obj_root, 'v1')))
            print(os.listdir(os.path.join(obj_root, 'v1', 'content')))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Migrate Fedora3 repository to OCFL storage root')
    parser.add_argument('pid')
    args = parser.parse_args()
    migrate(args)

