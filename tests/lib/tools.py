""" General commands with no good home """
# pylint: disable=global-statement

from os.path import abspath, dirname, join

import time

PROJECT_FOLDER = dirname(dirname(dirname(abspath(__file__))))
TEST_FOLDER = join(PROJECT_FOLDER, 'tests')
DOCKER_FOLDER = join(TEST_FOLDER, 'docker')

def wait_for(condition):
    """ Waits for a condition to become true, returning True if it ever does """

    for _ in range(120):
        if condition():
            return True
        time.sleep(1)

LONGEST_MESSAGE = 0
def show_status(message, newline=False):
    """ Pretty print a status message """

    global LONGEST_MESSAGE

    print(message, end='')
    LONGEST_MESSAGE = max(LONGEST_MESSAGE, len(message))
    print(' ' * (LONGEST_MESSAGE - len(message)), end='\n' if newline else '\r')

def show_result(version, name, success):
    """ Show the result of a test """

    print('PostgreSQL {version}: Test {name} - {result}'.format(
        version=version, name=name, result='PASS' if success else 'FAIL'
    ))

    return success
