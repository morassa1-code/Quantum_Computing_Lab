#####################
# OPX configuration #
#####################
IF = 10e6
LO = 8.8e9
con = "con1"
octave = "oct1"
qop_ip = "10.4.1.2"
cluster_name = "Cluster_1"
qop_port = None
config = {
    "controllers": {
        con: {
            "analog_outputs": {
                1: {"offset": 0.0},
                2: {"offset": 0.0},
                3: {"offset": 0.0},
                4: {"offset": 0.0},
                5: {"offset": 0.0},
                6: {"offset": 0.0},
                7: {"offset": 0.0},
                8: {"offset": 0.0},
                9: {"offset": 0.0},
                10: {"offset": 0.0},
            },
            "digital_outputs": {
                1: {},
                3: {},
                5: {},
                7: {},
                9: {},
            },
            "analog_inputs": {
                1: {"offset": 0.0},
                2: {"offset": 0.0},
            },
        }
    },
    "elements": {
        "qe1": {
            "RF_inputs": {"port": (octave, 1)},
            "RF_outputs": {"port": (octave, 1)},
            "intermediate_frequency": IF,
            "operations": {
                "cw": "const",
                "readout": "readout_pulse",
            },
            "digitalInputs": {
                "switch": {
                    "port": (con, 1),
                    "delay": 87,
                    "buffer": 15,
                },
            },
            "time_of_flight": 200,
            "smearing": 0,
        },
        "qe2": {
            "RF_inputs": {"port": (octave, 2)},
            "RF_outputs": {"port": (octave, 2)},
            "intermediate_frequency": IF,
            "operations": {
                "cw": "const",
                "readout": "readout_pulse",
            },
            "digitalInputs": {
                "switch": {
                    "port": (con, 3),
                    "delay": 87,
                    "buffer": 15,
                },
            },
            "time_of_flight": 100,
            "smearing": 0,
        },
        "qe3": {
            "RF_inputs": {"port": (octave, 3)},
            "intermediate_frequency": IF,
            "operations": {
                "cw": "const",
                "readout": "readout_pulse",
            },
            "digitalInputs": {
                "switch": {
                    "port": (con, 5),
                    "delay": 136,
                    "buffer": 0,
                },
            },
        }
        ,
        "qe10": {
            "singleInput":{"port": (con, 10)},
            "outputs": {"output1": (con, 1)},
            "intermediate_frequency": IF,
            "operations": {
                "cw": "const_single",
                "readout": "readout_pulse_raw",
            },
            "time_of_flight": 200,
            "smearing": 0,
        },
        "qe11": {
            "singleInput":{"port": (con, 10)},
            "intermediate_frequency": IF,
            "operations": {
                "cw": "const_single",
                "readout": "readout_pulse_raw",
            },
        },
        "qe12": {
            "singleInput":{"port": (con, 10)},
            "intermediate_frequency": IF,
            "operations": {
                "cw": "const_single",
                "readout": "readout_pulse_raw",
            },
        }
    },
    "octaves": {
        octave: {
            "RF_outputs": {
                1: {
                    "LO_frequency": LO,
                    "LO_source": "internal",  # can be external or internal. internal is the default
                    "output_mode": "always_on",  # can be: "always_on" / "always_off"/ "triggered" / "triggered_reversed". "always_off" is the default
                    "gain": 0,  # can be in the range [-20 : 0.5 : 20]dB
                },
                2: {
                    "LO_frequency": LO,
                    "LO_source": "internal",
                    "output_mode": "always_on",
                    "gain": 0,
                },
                3: {
                    "LO_frequency": LO,
                    "LO_source": "internal",
                    "output_mode": "always_on",
                    "gain": 10,
                },
                4: {
                    "LO_frequency": LO,
                    "LO_source": "internal",
                    "output_mode": "always_on",
                    "gain": 0,
                },
                5: {
                    "LO_frequency": LO,
                    "LO_source": "internal",
                    "output_mode": "always_on",
                    "gain": 0,
                },
            },
            "RF_inputs": {
                1: {
                    "LO_frequency": LO,
                    "LO_source": "internal",  # internal is the default
                    "IF_mode_I": "direct",  # can be: "direct" / "mixer" / "envelope" / "off". direct is default
                    "IF_mode_Q": "direct",
                },
                2: {
                    "LO_frequency": LO,
                    "LO_source": "internal",  # external is the default
                    "IF_mode_I": "direct",
                    "IF_mode_Q": "direct",
                },
            },
            "connectivity": con,
        }
    },
    
    "pulses": {
        "const": {
            "operation": "control",
            "length": 1000,
            "waveforms": {
                "I": "const_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
        },
        "readout_pulse": {
            "operation": "measurement",
            "length": 2000,
            "waveforms": {
                "I": "readout_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "cos": "cosine_weights",
                "sin": "sine_weights",
                "minus_sin": "minus_sine_weights",
            },
            "digital_marker": "ON",
        },
        "readout_pulse_raw": {
            "operation": "measurement",
            "length": 2000,
            "waveforms": {"single": "const_wf"},
            "digital_marker": "ON",
            "integration_weights": {"cos": "cosine_weights", "sin": "sine_weights"},
        },
        "const_single": {
            "operation": "control",
            "length": 1000,
            "waveforms": {
                "single": "const_wf", # Note the key is "single"
            },
            "digital_marker": "ON",
        }
    },
    "waveforms": {
        "zero_wf": {
            "type": "constant",
            "sample": 0.0,
        },
        "const_wf": {
            "type": "constant",
            "sample": 0.125,
        },
        "readout_wf": {
            "type": "constant",
            "sample": 0.125,
        },
    },
    "digital_waveforms": {
        "ON": {"samples": [(1, 0)]},
        "OFF": {"samples": [(0, 0)]},
    },
    "integration_weights": {
        "cosine_weights": {
            "cosine": [(1.0, 1000)],
            "sine": [(0.0, 1000)],
        },
        "sine_weights": {
            "cosine": [(0.0, 1000)],
            "sine": [(1.0, 1000)],
        },
        "minus_sine_weights": {
            "cosine": [(0.0, 1000)],
            "sine": [(-1.0, 1000)],
        },
    },
}