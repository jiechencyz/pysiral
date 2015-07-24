# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 15:10:04 2015

@author: Stefan
"""

from pysiral.cryosat2.functions import (
    get_structarr_attr, tai2utc, get_tai_datetime_from_timestamp,
    get_cryosat2_wfm_power, get_cryosat2_wfm_range)
from pysiral.cryosat2.l1bfile import CryoSatL1B
from pysiral.helper import parse_datetime_str

import numpy as np


class L1bAdapterCryoSat(object):
    """ Converts a CryoSat2 L1b object into a L1bData object """
    def __init__(self, config):
        self.filename = None
        self._config = config
        self._mission = "cryosat2"

    def construct_l1b(self, l1bdata):
        # Store the pointer to the L1bData object
        self.l1bdata = l1bdata
        # Read the CryoSat-2 L1b data file
        self._read_cryosat2l1b()
        # Transfer Metdata
        self._transfer_metadata()
        # Transfer the time and orbit data
        self._transfer_timeorbit()
        # Transfer the waveform data
        self._transfer_waveform_collection()
        # Transfer the range corrections
        self._transfer_range_corrections()
        # Transfer any classifier data
        self._transfer_classifiers()

    def _read_cryosat2l1b(self):
        """ Read the L1b file and create a CryoSat-2 native L1b object """
        self.cs2l1b = CryoSatL1B()
        self.cs2l1b.filename = self.filename
        self.cs2l1b.parse()
        error_status = self.cs2l1b.get_status()
        if error_status:
            # TODO: Needs ErrorHandler
            raise IOError()
        self.cs2l1b.post_processing()

    def _transfer_metadata(self):
        self.l1bdata.info.mission = self._mission
        self.l1bdata.info.mission_data_version = self.cs2l1b.baseline
        self.l1bdata.info.radar_mode = self.cs2l1b.radar_mode
        self.l1bdata.info.orbit = self.cs2l1b.sph.abs_orbit_start
        self.l1bdata.info.start_time = parse_datetime_str(
            self.cs2l1b.sph.start_record_tai_time)
        self.l1bdata.info.stop_time = parse_datetime_str(
            self.cs2l1b.sph.stop_record_tai_time)

    def _transfer_timeorbit(self):
        # Transfer the orbit position
        longitude = get_structarr_attr(self.cs2l1b.time_orbit, "longitude")
        latitude = get_structarr_attr(self.cs2l1b.time_orbit, "latitude")
        altitude = get_structarr_attr(self.cs2l1b.time_orbit, "altitude")
        self.l1bdata.time_orbit.set_position(longitude, latitude, altitude)
        # Transfer the timestamp
        tai_objects = get_structarr_attr(
            self.cs2l1b.time_orbit, "tai_timestamp")
        tai_timestamp = get_tai_datetime_from_timestamp(tai_objects)
        utc_timestamp = tai2utc(tai_timestamp)
        self.l1bdata.time_orbit.timestamp = utc_timestamp

    def _transfer_waveform_collection(self):
        # Create the numpy arrays for power & range
        n_records = len(self.cs2l1b.waveform)
        n_range_bins = len(self.cs2l1b.waveform[0].wfm)
        echo_power = np.ndarray(shape=(n_records, n_range_bins))
        echo_range = np.ndarray(shape=(n_records, n_range_bins))
        # Set the echo power in dB and calculate range
        for i, record in enumerate(self.cs2l1b.waveform):
            echo_power[i, :] = get_cryosat2_wfm_power(
                np.array(record.wfm).astype(np.float32),
                record.linear_scale, record.power_scale)
            echo_range[i, :] = get_cryosat2_wfm_range(
                self.cs2l1b.measurement[i].window_delay, n_range_bins)
        # Transfer to L1bData
        self.l1bdata.waveform.add_waveforms(echo_power, echo_range)

    def _transfer_range_corrections(self):
        # Transfer all the correction in the list
        for key in self.cs2l1b.corrections[0].keys():
            if key in self._config.parameter.correction_list:
                self.l1bdata.correction.set_parameter(
                    key, get_structarr_attr(self.cs2l1b.corrections, key))
        # CryoSat-2 specific: Two different sources of ionospheric corrections
        options = self._config.get_mission_defaults(self._mission)
        key = options["ionospheric_correction_source"]
        ionospheric = get_structarr_attr(self.cs2l1b.corrections, key)
        self.l1bdata.correction.set_parameter("ionospheric", ionospheric)

    def _transfer_classifiers(self):
        # Add potential surface type classifiers

        # L1b surface type flag word
        self.l1bdata.classifier.add_parameter(
            "l1b_surface_type",
            get_structarr_attr(self.cs2l1b.corrections, "surface_type"),
            "surface_type")
        # Add a selection of beam parameters to the list of surface type
        # classifiers
        beam_parameter_list = ["stack_standard_deviation",
                               "stack_centre",
                               "stack_scaled_amplitude",
                               "stack_skewness",
                               "stack_kurtosis"]
        for beam_parameter_name in beam_parameter_list:
            recs = get_structarr_attr(self.cs2l1b.waveform, "beam")
            beam_parameter = [rec[beam_parameter_name] for rec in recs]
            self.l1bdata.classifier.add_parameter(
                beam_parameter_name, beam_parameter, "surface_type")