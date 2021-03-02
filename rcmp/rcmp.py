# rcmp.rcmp

import os.path
import sys
from threading import Thread
import time
import mido

import rcmp.media
import rcmp.options
import rcmp.oschandler
import rcmp.docs

APP = None

class Rcmp:

    def __init__(self):
        self._osc_poll_thread = None
        self._osc_handler = None
        self._midi_backend = None
        self._midi_output_name = None
        self._midi_output_port = None
        self._osc_ip = None
        self._osc_port = None
        self._osc_prefix = None
        self._auto_exit = False
        self.stop_signal = True
        self.exit_signal = False
        self.media_list = rcmp.media.MediaList(self)
        
    @property
    def midi_backend(self):
        return self._midi_backend

    @property
    def midi_output_name(self):
        return self._midi_output_name

    @property
    def midi_output_port(self):
        return self._midi_output_port

    @property
    def osc_ip(self):
        return self._osc_ip

    @property
    def osc_port(self):
        return self._osc_port

    @property
    def osc_prefix(self):
        return self._osc_prefix

    def _osc_poll_callback(self, *args):
        while not self.exit_signal:
            self._osc_handler.poll()

    def _start_osc_poll_loop(self):
        if not self._osc_poll_thread:
            self._osc_poll_thread = Thread(target=self._osc_poll_callback, daemon=True)
            self._osc_poll_thread.start()

    def print_prompt(self):
        print(f"{self.osc_prefix} : ", end = "", flush = True)
            
    def midi_reset(self):

        def controller(channel, controller, value):
            msg = mido.Message("control_change", channel=channel, control=controller, value=value)
            self._midi_output_port.send(msg)
            
        self._midi_output_port.send(mido.Message("reset"))
        for c in range(0, 16):
            controller(c, 1, 0)     # reset modulation wheel
            controller(c, 69, 0)    # sustain pedal off
            controller(c, 123, 127) # all notes off
            controller(c, 10, 127)  # volume
            for key in range(0, 128):
                msg = mido.Message("note_off", channel=c, note=key)
                self._midi_output_port.send(msg)
                if key % 10 == 0:
                    time.sleep(0.001)

    def _play_mode_loop(self):
        midi_file = self.media_list.midi_file()
        note_queue = []
        if midi_file and self._midi_output_port:
            for msg in midi_file:
                time.sleep(msg.time)
                if not msg.is_meta:
                    self._midi_output_port.send(msg)
                    typ = msg.type
                    if typ == "note_on" and msg.velocity > 0:
                        note_queue.append((msg.channel, msg.note))
                    elif typ == "note_off" or (typ=="note_on" and msg.velocity==0):
                        note_queue.remove((msg.channel, msg.note))
                if self.stop_signal or self.exit_signal:
                    break
                
            self.stop_signal = True
            # Kill all notes in queue
            for chan, key in note_queue:
                msg = mido.Message("note_off", channel=chan, note=key)
                self._midi_output_port.send(msg)
                time.sleep(0.001)
            if self._auto_exit:
                self.exit(0)
            else:
                self.midi_reset()

    def _stop_mode_loop(self):
        while self.stop_signal and not self.exit_signal:
            pass

    def mainloop(self):
        while not self.exit_signal:
            if self.stop_signal:
                self._stop_mode_loop()
            else:
                self._play_mode_loop()
        self.exit()
                
    def _configure_media_list(self, name, is_file):
        if name and name[0] == '-':
            return
        if name and is_file:
            abspath = os.path.abspath(name)
            alias  = os.path.splitext(os.path.basename(abspath))[0]
            parent = os.path.split(abspath)[0]
            self.media_list.scan_directory(parent)
            self.media_list.select(alias)
        elif name and not is_file:
            abspath = os.path.abspath(name)
            self.media_list.scan_directory(abspath)
            lst = self.media_list.aliases
            if lst:
                self.media_list.select(lst[0])

    def dump(self):
        print("Rcmp application state:")
        print(f"\tself._midi_backend      --> {self._midi_backend}")
        print(f"\tself._midi_output_name  --> {self._midi_output_name}")
        print(f"\tself._midi_output_port  --> {self._midi_output_port}")
        print(f"\tself._osc_ip            --> {self._osc_ip}")
        print(f"\tself._osc_port          --> {self._osc_port}")
        print(f"\tself._osc_prefix        --> {self._osc_prefix}")
        print(f"\tself.stop_signal        --> {self.stop_signal}")
        print(f"\tself.exit_signal        --> {self.exit_signal}")
        print(f"\tself._auto_exit         --> {self._auto_exit}")
        self.media_list.dump()

    def exit(self, code=0):
        print("Exit\n", flush=True)
        self.midi_reset()
        self._osc_handler.close()
        raise SystemExit()
        
    @classmethod
    def _configure_midi_backend(cls, app, args):
        app._midi_backend = args["backend"]
        mido.set_backend(app._midi_backend)

    @classmethod
    def _use_default_midi_output(cls, app, outputs):
        if outputs:
            name = outputs[0]
            port = mido.open_output(name)
            app._midi_output_name = name
            app._midi_output_port = port
        else:
            print("ERROR Can not set MIDI output")
            sys.exit(1)
            
    @classmethod
    def _configure_midi_output(cls, app, args):
        outputs = mido.get_output_names()
        out = args["out"]
        name = port = None
        try:
            n = int(out)
            if 0 <= n < len(outputs):
                name = outputs[n]
                app._midi_output_name = name
                app._midi_output_port = mido.open_output(name)
            else:
                print(f"WARNING: Invalid MIDI output number: {n}, using default 0.")
                cls._use_default_midi_output(app, outputs)
                port = mido.open_output(name)
        except ValueError:  # Select port by name
            try:
                name = out
                port = mido.open_output(name)
                app._midi_output_name = name
                app._midi_output_port = port
            except OSError:
                print(f"WARNING: Invalid MIDI output name: '{out}', using default.")
                cls._use_default_midi_output(app, outputs)
        print(f"MIDI BACKEND: '{app._midi_backend}'  OUTPUT: '{app._midi_output_name}'")
                
    @classmethod
    def _configure_osc(cls, app, args):
        app._osc_port = int(args["port"])
        app._osc_ip = args["ip"]
        app._osc_prefix = args["osc"]
        app._osc_handler = rcmp.oschandler.OSCHandler(app)
             
    @classmethod
    def list_midi_outputs(cls, app):
        print(f"MIDI backend: '{app._midi_backend}'")
        print(f"Available MIDI Outputs:")
        for i, name in enumerate(mido.get_output_names()):
            print(f"\t[{i}]  '{name}'")
        sys.exit(0)
        
    @classmethod
    def run(cls, argv):
        global APP
        APP = Rcmp()
        parser = rcmp.options.create_argparse()
        file_argument, is_file, argv = rcmp.options.extract_file_argument(argv)
        args = vars(parser.parse_args(argv))
        APP._configure_media_list(file_argument, is_file)
        
        if args["docs"]:
            print(rcmp.docs.DOCS)
            sys.exit(0)
        
        APP._auto_exit = args["exit"]
        cls._configure_midi_backend(APP, args)

        if args["list"]:
            cls.list_midi_outputs(APP)
        
        cls._configure_midi_output(APP, args)
        cls._configure_osc(APP, args)
        
        if args["play"] and APP.media_list.current_item:
            APP.stop_signal = False
        APP._start_osc_poll_loop()
        APP.print_prompt()
        APP.mainloop()
        
