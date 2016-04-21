# -*- coding: utf-8 -*-
"""
Created on Thu Apr 07 16:19:41 2016

@author: shendric
"""


class GridMapParameterBase(object):
    """
    Contains data, pcolor grid calculation capability, colormap definition
    and standardized parameter naming
    """

    def __init__(self):
        from pysiral.config import get_parameter_definitions
        self._parameter_definitions = get_parameter_definitions()
        self._projection = None
        self.latitude = None
        self.longitude = None
        self.grid = None
        self.pgrid = None
        self.pardef = None

    def set_grid(self, longitude, latitude):
        self.longitude = longitude
        self.latitude = latitude

    def set_projection(self, **projection):
        from pysiral.maptools import GeoPcolorGrid
        self.pgrid = GeoPcolorGrid(self.longitude, self.latitude)
        self.pgrid.calc_from_proj(**projection)


class GridMapParameter(GridMapParameterBase):

    def __init__(self):
        super(GridMapParameter, self).__init__()

    def get_cmap(self):
        return self.pardef.cmap

    def get_label(self):
        return self.pardef.label+" ("+self.pardef.unit+")"

    def set_parameter(self, grid, parameter_name):
        self.grid = grid
        self.pardef = self._parameter_definitions[parameter_name]


class GridMapDiffParameter(GridMapParameterBase):
    """
    Contains data, pcolor grid calculation capability, colormap definition
    and standardized parameter naming
    """

    def __init__(self):
        super(GridMapDiffParameter, self).__init__()

    def get_cmap(self):
        return self.pardef.cmap_diff

    def get_label(self):
        return "$\Delta$ "+self.pardef.label+" ("+self.pardef.unit+")"

    def set_parameter(self, grida, gridb, parameter_name):
        self.grid = gridb-grida
        self.pardef = self._parameter_definitions[parameter_name]