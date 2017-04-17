from os.path import abspath, dirname, join

import time

PROJECT_FOLDER=dirname(dirname(dirname(abspath(__file__))))
TEST_FOLDER=join(PROJECT_FOLDER, 'tests')
DOCKER_FOLDER=join(TEST_FOLDER, 'docker')

def wait_for(condition):
    for i in range(120):
        if condition():
            return True
        time.sleep(1)
