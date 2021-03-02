# rcmp application launcer.
# 
# Usage python3 main.py [options] [midifile-or-directory]
#

import sys

if __name__ == "__main__":
    from rcmp.rcmp import Rcmp
    Rcmp.run(sys.argv)
    sys.exit(0)

    
