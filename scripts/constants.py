import os

__DEFAULT_CONFIG_DIR = 'src/configurations'
CONFIG_DIR = __DEFAULT_CONFIG_DIR

if 'CONFIG_DIR' in os.environ:
  CONFIG_DIR = os.environ['CONFIG_DIR']

TEST_INTEGRATION_NAME_PREFIX = 'test_'

TEST_INTEGRATION_NAME_SUFFIX = '_ignore'
