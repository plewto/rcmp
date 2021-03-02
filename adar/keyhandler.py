
HELP_TEXT = """
Adar KEYBAORD COMMANDS:
  0-9 Number keys select corresponding item from the media-list.
  h - help
  i - Display info about currently selected file.
  p - start playback
  s - stop playback
  c - clear screen
  q - quit Adar
  space - toggle play/stop
"""

class KeyHandler:

    def __init__(self, app):
        self.app = app
 
    def poll(self):
        return ""
            
    def close(self):
        pass
        
