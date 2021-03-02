# adar.options
#
# Configures argparse

import argparse
import os.path


def create_argparse():
    parser = argparse.ArgumentParser(description="Play MIDI files under OSC control.")

    parser.add_argument("-i", "--info", default=False, action="store_true",
                        help="Print information about MIDI file and exit.")

    parser.add_argument("-l", "--list", default=False, action="store_true",
                        help="List available MIDI outputs.")

    parser.add_argument("--docs", default=False, action="store_true",
                        help="Display more detailed help.")

    parser.add_argument("-b", "--backend", type=str, default="mido.backends.portmidi",
                        help="Set MIDI backend, see documentation for mido.")

    parser.add_argument("-o", "--out", type=str, default="0",
                        help="Select MIDI output, either by name or number.")

    parser.add_argument("--port", type=int, default=7000,
                        help="Set OSC port number.")

    parser.add_argument("--osc", type=str, default="/adar",
                        help="Set OSC address prefix.")

    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="OSC ip address")

    parser.add_argument("-x", "--exit", default=False, action="store_true",
                        help="Exit program after playing file,  exit only makes sense when --play option is present.")

    parser.add_argument("-p", "--play", default=False, action="store_true",
                        help="Start playback of initial file immediately.")

    return parser




def _is_file(s): 
    return os.path.exists(s) and os.path.isfile(s)

def _is_directory(s):
    return os.path.exists(s) and os.path.isdir(s)

def extract_file_argument(argv):
    if len(argv) > 1:
        final = argv[-1]
        if _is_file(final):
            return final, True, argv[1:-1]
        elif _is_directory(final):
            return final, False, argv[1:-1]
        else:
            return final, False, argv
    else:
        return None, False, []
    
        
