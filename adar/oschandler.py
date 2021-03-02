# adar oschandler

import pyOSC3
import sys

class OSCHandler:

    def __init__(self, app):
        self.app = app
        adr = (app.osc_ip, app.osc_port)
        self.server = pyOSC3.OSCServer(adr)
        self.register("exit", self.exit_callback)
        self.register("play", self.play_callback)
        self.register("stop", self.stop_callback)
        self.register("list", self.media_list_callback)
        self.register("info", self.info_callback)
        self.register("select", self.select_callback)
        self.register("scan", self.scan_callback)
        
    def register(self, command, callback):
        adr = f"{self.app.osc_prefix}/{command}"
        self.server.addMsgHandler(adr, callback)
        
    def exit_callback(self, *args):
        self.app.stop_signal = True
        self.app.exit_signal = True

    def play_callback(self, *args):
        self.app.stop_signal = False

    def stop_callback(self, *args):
        self.app.stop_signal = True

    def media_list_callback(self, *args):
        self.app.media_list.dump()
        print()

    def info_callback(self, *args):
        print("Info")
        print(f"MIDI Output: '{self.app.midi_output_name}'")
        print(self.app.media_list.selected_file_info())
        print()
              
    def select_callback(self, *args):
        alias = args[2][0]
        print(f"Select '{alias}'")
        self.app.media_list.select(alias)
        self.app.media_list.dump()
        
    def scan_callback(self, *args):
        directory = args[2][0]
        print(f"Scanning directory '{directory}'")
        self.app.media_list.scan_directory(directory)
        self.app.media_list.dump()
        
        
    def poll(self):
        self.server.handle_request()
    

    
