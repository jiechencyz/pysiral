# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 14:04:27 2015

@author: Stefan
"""
from pysiral.l1bdata import L1bConstructor
from pysiral.l2data import Level2Data


class Level2Processor(object):

    def __init__(self, job):

        self._job = job
        self._orbit = []
        self._config = None
        self._error_handler = {"raise_on_error": True}

    def error_handling(self, **keyw):
        self.error_handler.update(keyw)

    def set_config(self, config):
        self._config = config

    def run(self):
        """ Run the processor """
        self._initiatize_processor()
        self._run_processor()
        self._clean_up()

    def purge(self):
        """ Clean the orbit collection """
        pass

    def grid_orbit_collection(self, grid_definitions):
        pass

    def _initialize_processor(self):
        """ Read required auxiliary data sets """
        # TODO: Check if already inizialized
        pass

    def _run_processor(self):
        """ Orbit-wise level2 processing """
        # TODO: Evaluate parallelization
        for l1b_file in self._job.l1b_files:
            l1b = self._read_l1b_file(l1b_file)
            in_roi = self._trim_to_roi(l1b)
            if not in_roi:
                continue
            self._range_corrections(l1b)
            l2 = Level2Data()
            self._classify_surface_type(l1b, l2)
            self._retrack_waveforms(l1b, l2)        # -> Elevations
            self._reference_to_ssh(l2)              # -> Radar Freeboard
            self._apply_data_quality_filter(l2)
            self._post_processing(l2)
            self._create_outputs(l2)
            self._add_to_orbit_collection(l2)

    def _clean_up(self):
        """ Make sure to deallocate memory """
        pass

    def _read_l1b_file(self, l1b_file):
        """ Read a L1b data file """
        l1b = L1bConstructor(self._config)
        l1b.mission = self._job.mission.id
        l1b.set_mission_options(self._job.mission.options)
        l1b.filename = l1b_file
        l1b.construct()
        return l1b

    def _trim_roi(self, l1b):
        """ Trims orbit for ice/ocean areas """
        return True

    def _retrack_waveforms(self, l1b):
        pass

    def _reference_to_ssh(self, l2):
        pass

    def _apply_data_quality_filter(self, l2):
        pass

    def _post_processing(self, l2):
        pass

    def _create_outputs(self, l2):
        pass

    def _add_to_orbit_collection(self, l2):
        pass