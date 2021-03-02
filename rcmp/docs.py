# rcmp.docs


USAGE = """
USAGE:
    python3 main.py [options...] [file]

    If the optional file is specified it should either be a MIDI file 
    or a directory containing MIDI files.   

    If file names a directory, the MIDI file contents of the directory
    are added to the media-list and the first file is selected.

    If file names a MIDI file, the parent directory is added to the 
    media-list and file is selected for playback.

    If the --play option is present rcmp immediately starts playback 
    of the selected MIDI file.

    If the --exit option is present, rcmp will exit immediately after 
    playing the initial MIDI file.  Otherwise, it enters a loop 
    and waits for OSC commands.    To terminate the program send
    the OSC message /rcmp/exit

    NOTE: rcmp currently only handles single-track, type 0, MIDI files.

    -h --help
             Display auto-generated command-line help and exit.

       --docs
             Display detailed documentation and exit.

    -l --list
             List available MIDI outputs and exit.

    -o --out device
             Selects MIDI output, use --list for possible values.
             device may either be the numeric position in the list
             or the exact device name.  If the name is used it will 
             probably need to be quoted.  Defaults to 0.
             
    -b --backend
            Sets MIDI backend.  See mido documentation.
            Defaults to 'mido.backends.portmidi'
           
       --port
            Sets OSC port number, default 7000.

       --osc
           Sets OSC path prefix.  All OSC commands must begin
           with this prefix, default '/rcmp'

       --ip
           Sets OSC server ip address, default 127.0.0.1

    -p --play
           Immediately play the MIDI file specified by the optional 
           file argument.  The --play option is ignored if the file
           argument is not present.
 
    -x --exit
           Immediately exit the program after playing the initial file.
           --exit only makes sense in conjunction with the --play
           option.
"""


OSC_COMMANDS = """
OSC COMMANDS:

    /rcmp/exit
        Terminate rcmp.
        
    /rcmp/play
        Start playback of selected MIDI file.
        
    /rcmp/stop
        Stop playback, there may be a few seconds delay
        before the playback halts.
        
    /rcmp/list
        Display the media-list, an asterisk indicates the currently 
        selected file.
        
    /rcmp/info
        Display details about currently selected MIDI file.
        
    /rcmp/scan directory
        First clear the media list.  Then, load each MIDI file 
        in directory into the media-list.
        
    /rcmp/select file
        Select file from media-list. The file may be specified either
        by it's position in the media-list, or by name.  If the name 
        is used, do not include filename extension.
    
    /rcmp/help
        Display this message.

"""

DOCS = """
NAME
    rcmp is a termonal based MIDI file player with OSC control.

""" + USAGE + OSC_COMMANDS
