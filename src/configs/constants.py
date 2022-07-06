import os
import getpass

PROJECT_SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = os.path.dirname(PROJECT_SRC_ROOT)

RUNNER_USERNAME = getpass.getuser()


if __name__ == '__main__':
    print('user: %s' % RUNNER_USERNAME)
    print('project root: %s' % PROJECT_ROOT)
