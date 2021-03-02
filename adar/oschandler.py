# adar oschandler

import pyOSC3
import sys

class OSCHandler:

    def __init__(self, app):
        self.app = app
        adr = (app.osc_ip, app.osc_port)
        self.server = pyOSC3.OSCServer(adr)
        self.register("exit", self.exit_handler)

    def register(self, command, callback):
        adr = f"{self.app.osc_prefix}/{command}"
        self.server.addMsgHandler(adr, callback)
        
    def exit_handler(self, *args):
        self.app.stop_signal = True
        self.app.exit_signal = True

    def play_callback(self, *args):
        self.app.stop_signal = False
        
    def poll(self):
        self.server.handle_request()
    

    
