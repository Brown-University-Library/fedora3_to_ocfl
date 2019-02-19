import os
from eulfedora.server import Repository


def get_env_variable(var):
    try:
        return os.environ[var]
    except KeyError:
        raise Exception(f'missing {var} environment variable')


FEDORA_ROOT = get_env_variable('FEDORA_ROOT')
FEDORA_USERNAME = get_env_variable('FEDORA_USERNAME')
FEDORA_PASSWORD = get_env_variable('FEDORA_PASSWORD')

REPO = Repository(root=FEDORA_ROOT, username=FEDORA_USERNAME, password=FEDORA_PASSWORD)

