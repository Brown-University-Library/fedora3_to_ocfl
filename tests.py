import io
import json
import os
import tempfile
import unittest
from settings import REPO
import migrate


class TestMigrate(unittest.TestCase):

    def setUp(self):
        obj = REPO.get_object(create=True)
        obj.default_pidspace = 'testsuite'
        obj.save()
        self.pid = obj.pid

    def test_basic(self):
        #migrate
        with tempfile.TemporaryDirectory() as tmp_dir:
            migrate.migrate(self.pid, tmp_dir)
            #verify
            self.assertEqual(os.listdir(tmp_dir), [self.pid])
            with open(os.path.join(tmp_dir, self.pid, 'inventory.json'), 'rb') as f:
                inventory = json.loads(f.read().decode('utf8'))
            self.assertEqual(list(inventory['versions'].keys()), ['v1'])
            self.assertEqual(len(inventory['manifest'].keys()), 2)
            content_dir = os.path.join(tmp_dir, self.pid, 'v1', 'content')
            self.assertEqual(os.listdir(content_dir), ['RELS-EXT', 'DC'])
        #cleanup
        REPO.api.purgeObject(self.pid)

    def test_obj_already_exists(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.mkdir(os.path.join(tmp_dir, self.pid))
            with self.assertRaises(migrate.MigrationError):
                migrate.migrate(self.pid, tmp_dir)


if __name__ == '__main__':
    unittest.main()

