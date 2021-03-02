# adar.media
#
# Defines MediaItem and MediaList classes.
#

import os
import os.path as path
import mido

class MediaItem:

    """Provides a MIDI file alias."""
    
    def __init__(self, filename, alias=None):
        """
        Constructs new instance of MediaItem.

            Parameters:
                filename (str): A MIDI file filename.
                alias (str): An optional alias for filename, defaults to the basename without extension.
         """
        
        self._filename = filename
        if alias:
            self._alias = alias
        else:
            self._alias = path.splitext(path.basename(filename))[0]

    @property
    def filename(self):
        return self._filename

    @property
    def alias(self):
        return self._alias

    @property
    def midi_file(self):
        """
        Returns an instance of mido.MidiFile for self.filename.

        If either the file does not exists, or it is not a MIDI file, 
        prints warning and returns None.
        """
        try:
            return mido.MidiFile(self.filename)
        except OSError:
            msg = f"ERROR: Either '{self.filename}'\n"
            msg += "ERROR: does not exists or it is not a MIDI file."
            # print(msg)  # Do not directly call print, use Keyhandler print function.
            return None

    def __str__(self):
        frmt = "{0:16} --> {1}"
        return frmt.format(self.alias, self.filename)


class MediaList:

    """
    Maintains list of all MIDI files within a directory.

    At any one time, one of the files is marked as 'selected'.
    """

    EXTENSIONS = [".mid", ".syx"]

    @classmethod
    def accept(cls, filename):
        """
        Determine if filename has expected extension.

            Parameters:
               filename (str)

            Returns: 
               True iff the filename extension is a recognized MIDI file.
               The test is case insensitive.
        """
        
        ext = path.splitext(filename)[-1].lower()
        return ext in cls.EXTENSIONS
    
    def __init__(self, app, directory=None):
        """
        Constructs new instance of MediaList.

            Parameters:
                directory (str): Optional directory name
                    If specified, the list is populated with all MIDI files found within 
                    the directory and the first file is 'selected'. 
        """
        self.app = app
        self._items = {}
        self._directory = None
        self._current_item = None
       

    @property
    def current_item(self):
        return self._current_item
            
    def add(self, filename):
        """
        Adds new item to the list.

            Parameters:
                filename (str): The filename is added iff it is determined to be a MIDI file.
                The filename extension is ignored.
        """
        mi = MediaItem(filename)
        if mi.midi_file:
            self._items[mi.alias] = mi

    # Automatically marks the first filename as 'selected',
    # but only if there is not a currently selected file.
    def _auto_select(self):
        if not self._current_item:
            alist = self.aliases
            if len(alist):
                self.select(alist[0])
            
    def scan_directory(self, directory):
        """
        Clears the list and then adds all MIDI files in directory.
            
        If there is no current file, the first MIDI file in the directory is
        selected.

            Parameters:
               directory (str): Name of directory

            Returns:
               False if directory could no be read.
               True if directory contents were read.
        """

        rs = False
        self.clear()
        try:
            for file_name in os.listdir(directory):
                if self.accept(file_name):
                    self.add(path.join(directory, file_name))
                    self._directory = directory
            self._auto_select()
            rs = True
        except IOError:
            msg = f"ERROR: Can not scan directory: '{directory}'"
            print(msg)
        finally:
            return rs

    def clear(self):
        """Clears list contents."""
        self._items = {}
        self._directory = None
        self._current_item = None

    def rescan(self):
        """
        Updates list from the current directory.
        """
        if self._directory:
            temp_directory = self._directory
            temp_alias = None
            if self._current_item:
                temp_alias = self._current_item.alias
            self.clear()
            self.scan_directory(temp_directory)
            if temp_alias in self._items.keys():
                self.select(temp_alias)
            else:
                alist = self.aliases
                if len(alist):
                    self.select(alist[0])
        
    @property
    def aliases(self):
        """
        Returns sorted list of MIDI file names.
        """
        lst = list(self._items.keys())
        lst.sort()
        return lst
    
    def select(self, alias):
        """
        Marks selected file as 'selected'.

           Parameters:
              alias (str|int): MIDI filename alias or list-index.

           Returns:
              Either a matching MediaItem or, None is list does not contain alias.
        """
        rs = None
        try:
            n = int(alias)
            alist = self.aliases
            if 0 <= n < len(alist):
                alias = alist[n]
                self.select(alias)
        except ValueError:
            pass
        try:
            mi = self._items[alias]
            rs = self._current_item = mi
        except KeyError:
            msg = f"ERROR: Invalid media name: {alias}"
            print(msg)
        finally:
            return rs

    def midi_file(self, alias=None):
        """
        Retrieves MIDI file object for selected item.

        Parameters:
            alias (str): Optional string.
                If specified, alias becomes the currently selected MIDI file,
                defaults to the currently selected MIDI file.

        Returns:
            Either an instance of mido.MidiFile or, None if no item is selected.
        """
        rs = None
        if not alias:
            try:
                rs = self._current_item.midi_file
            except AttributeError:
                msg = f"ERROR: No media selected."
                print(msg)
        else:
            mi = self.select(alias)
            if mi:
                rs = mi.midi_file
        return rs
    
    def dump(self):
        """Displays list contents."""
        print("MediaList")
        print(f"Directory : {self._directory}")
        for n, a in enumerate(self.aliases):
            print("[{n:2d}] ".format(n=n), end="")
            mi = self._items[a]
            header = " " 
            if mi is self._current_item:
                header = "*"
            print(f"{header} {mi}")

    def selected_file_info(self):
        s = f"MIDI File: {self._current_item.filename}"
        return s
            
    def __str__(self):
        selected = "None"
        if self._current_item:
            selected = self._current_item.alias
        s = f"MediaList directory: '{self._directory}'  selected: {selected}"
        return s
