"""
Provides a ConfigParser object which provides all the settings for the ``PlantAnalyzer``
from the config-file ``analyzer.cfg``.

This ConfigParser object can be simultaneously used in different modules
"""

import ConfigParser
import os.path

if os.path.isfile('../analyzer.cfg'):
    config = ConfigParser.ConfigParser()
    config.read('../analyzer.cfg')  # should throw an exception, if it didn't work...

elif os.path.isfile('analyzer.cfg'):
    config = ConfigParser.ConfigParser()
    config.read('analyzer.cfg')     # should throw an exception, if it didn't work...

else:
    print("config file not found!")
