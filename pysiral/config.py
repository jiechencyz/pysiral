# -*- coding: utf-8 -*-
#
# Copyright © 2015 Stefan Hendricks
#
# Licensed under the terms of the GNU GENERAL PUBLIC LICENSE
#
# (see LICENSE for details)

"""
Purpose:
    Returns content of configuration and definition files

Created on Mon Jul 06 10:38:41 2015

@author: Stefan
"""

import os
import yaml
from treedict import TreeDict


class ConfigInfo(object):
    """
    Container for the content of the pysiral definition files
    (in pysiral/configration) and the local machine definition file
    (local_machine_definition.yaml)
    """

    # Global variables
    _DEFINITION_FILES = {
        "mission": "mission_def.yaml",
        "area": "area_def.yaml",
        "auxdata": "auxdata_def.yaml",
        "product": "product_def.yaml",
        "parameter": "parameter_def.yaml",
    }

    _LOCAL_MACHINE_DEF_FILE = "local_machine_def.yaml"

    def __init__(self):
        """ Read all definition files """
        # Store the main path on this machine
        self.pysiral_local_path = get_pysiral_local_path()
        # read the definition files in the config folder
        self._read_config_files()
        # read the local machine definition file
        self._read_local_machine_file()

    @property
    def doc_path(self):
        """ Returns the local path to the document folder"""
        return self._return_path("doc")

    @property
    def config_path(self):
        """ Returns the local path to the document folder"""
        return self._return_path("config")

    def _read_config_files(self):
        for key in self._DEFINITION_FILES.keys():
            content = get_yaml_config(
                os.path.join(
                    self.config_path,
                    self._DEFINITION_FILES[key]))
            setattr(self, key, content)

    def _read_local_machine_file(self):
        content = get_yaml_config(
            os.path.join(
                self.pysiral_local_path, self._LOCAL_MACHINE_DEF_FILE))
        setattr(self, "local_machine", content)

    def _return_path(self, subfolder):
        return os.path.join(self.pysiral_local_path, subfolder)


def get_yaml_config(filename, output="treedict"):
    """
    Parses the contents of a configuration file in .yaml format
    and returns the content in various formats

    Arguments:
        filename (str)
            path the configuration file

    Keywords:
        output (str)
            "treedict" (default): Returns a treedict object
            "dict": Returns a python dictionary
    """
    with open(filename, 'r') as f:
        content_dict = yaml.load(f)

    if output == "treedict":
        return TreeDict.fromdict(content_dict, expand_nested=True)
    else:
        return content_dict


def get_pysiral_local_path():
    """ Returns pysiral's main directory for the local machine """
    directory = os.path.dirname(__file__)
    directory = os.path.abspath(os.path.join(directory, '..'))
    return directory