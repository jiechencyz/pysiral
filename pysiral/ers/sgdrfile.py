# -*- coding: utf-8 -*-

from pysiral.errorhandler import FileIOErrorHandler

import numpy as np
import os


class ERSSGDR(object):

    def __init__(self, settings, raise_on_error=False):

        # Error Handling
        self._init_error_handling(raise_on_error)
        self._radar_mode = "lrm"
        self._filename = None
        self.n_records = 0
        self.settings = settings

    def parse(self):
        from pysiral.iotools import ReadNC
        self._validate()
        self.nc = ReadNC(self.filename, nan_fill_value=True)

    def guess_mission_from_filename(self):
        """
        This seems unnecessary, but some ERS-2 netCDF files have an incorrect mission attribute
        -> guess mission id from filename
        :return:
        """
        filename = os.path.split(self._filename)[-1]
        return filename[0:2]

    def get_status(self):
        # XXX: Not much functionality here
        return False

    def post_processing(self):
        """
        The SGDR data structure needs to be streamlined, so that it
        is easy to grab the relevant parameters as indiviual arrays
        """
        self._prepare_waveform_power_and_range()

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename):
        """ Save and validate filenames for header and product file """
        # Test if valid file first
        self._error.file_undefined = not os.path.isfile(filename)
        if self._error.file_undefined:
            return
        self._filename = filename

    @property
    def radar_mode(self):
        return self._radar_mode

    def _init_error_handling(self, raise_on_error):
        self._error = FileIOErrorHandler()
        self._error.raise_on_error = raise_on_error
        self._error.file_undefined = True

    def _prepare_waveform_power_and_range(self):
        """
        reforms the waveform to computes the corresponding range for each
        range bin
        """
        records_per_block, n_blocks, n_range_bins = self.nc.ku_wf.shape
        n_records = records_per_block*n_blocks
        self.n_records = n_records
        target_shape = (n_records, n_range_bins)
        self.wfm_power = np.reshape(self.nc.ku_wf, target_shape).astype(
            np.uint16)

        # Get the window delay
        # "The tracker_range_20hz is the range measured by the onboard tracker
        #  as the window delay, corrected for instrumental effects and
        #  CoG offset"
        tracker_range = self.nc.tracker_range_20hz.flatten()
        self.wfm_range = np.ndarray(shape=target_shape, dtype=np.float32)

        rbw = self.settings.range_bin_width
        ntb = self.settings.nominal_tracking_bin
        rbi = np.arange(n_range_bins)

        # Loop over each waveform
        for i in np.arange(n_records):
            self.wfm_range[i, :] = tracker_range[i] + (rbi*rbw) - (ntb*rbw)

    def _validate(self):
        pass
