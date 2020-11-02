# A Simple BitTorrent "bencode" Decoder

import sys
import re

class NofileException(Exception):
    """"Exception raised no filepath in sys.argv .

    Args:
        message (str): explanation of the error. Defaults to "No file found! Please pass file path as the first argument".
    """    
    def __init__(self, message="No file found! Please pass file path as the first argument"):      
        self.message = message
        super().__init__(self.message)


def decode(text):
    return text
    

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file = open(sys.argv[1], 'rb').read()

        torrent = decode(file)

        print(torrent)
    
    else: 
        raise NofileException()