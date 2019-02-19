import io
import json
import os
import tempfile
import unittest
from settings import REPO
import migrate


class TestMigrate(unittest.TestCase):

    def test_basic(self):
        #setup
        obj = REPO.get_object(create=True)
        obj.default_pidspace = 'testsuite'
        obj.save()
        #migrate
        with tempfile.TemporaryDirectory() as tmp_dir:
            migrate.migrate(obj.pid, tmp_dir)
            #verify
            self.assertEqual(os.listdir(tmp_dir), [obj.pid])
            with open(os.path.join(tmp_dir, obj.pid, 'inventory.json')) as f:
                inventory = json.loads(f.read())
            self.assertEqual(list(inventory['versions'].keys()), ['v1'])
            self.assertEqual(len(inventory['manifest'].keys()), 2)
            content_dir = os.path.join(tmp_dir, obj.pid, 'v1', 'content')
            self.assertEqual(os.listdir(content_dir), ['RELS-EXT', 'DC'])
        #cleanup
        REPO.api.purgeObject(obj.pid)


if __name__ == '__main__':
    unittest.main()

