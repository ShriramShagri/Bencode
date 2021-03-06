# A Simple BitTorrent "bencode" Decoder

# Repo: https://github.com/ShriramShagri/Bencode

import sys
import re
import hashlib
import os
import json

class InvalidFileException(Exception):
    """"Exception raised when invalid file path is given.

    Args:
        message (str): explanation of the error. Defaults to "No file found! Please pass file path as the first argument".
    """    
    def __init__(self, message="No .torrent file found! Please check path"):      
        self.message = message
        super().__init__(self.message)


def tokenize(text, match=re.compile("([idel])|(\d+):|(-?\d+)").match):
    """Creates usable generator out of items in the file

    Args:
        text (str): Contents of file
        match (function instance): Regex match function instance. Defaults to re.compile("([idel])|(\d+):|(-?\d+)").match.

    Yields:
        [str]: Elements in torrent file.
    """    
    i = 0
    while i < len(text):
        # Contents of file: integer, str or container(list/dict)
        m = match(text, i)
        s = m.group(m.lastindex)
        i = m.end()
        if m.lastindex == 2:
            # if string
            yield "s"
            # yield the actual string
            yield text[i:i+int(s)]
            # Skip the string
            i = i + int(s)
        else:
            yield s

def decode_item(next, token):
    """convert generator to dict/list

    Args:
        next (function): generator.__next__ function
        token (str): each individual tokens generated by tokenize function

    Raises:
        ValueError: Invalid Syntax... Error catched during function call.

    Returns:
        (dict, list): Decoded file
    """    
    if token == "i":
        # integer: "i" value "e"
        data = int(next())
        if next() != "e":
            raise ValueError
    elif token == "s":
        # string: "s" value (virtual tokens)
        data = next()
    elif token == "l" or token == "d":
        # container: "l" (or "d") values "e"
        data = []
        tok = next()
        while tok != "e":
            data.append(decode_item(next, tok))
            tok = next()
        if token == "d":
            data = dict(zip(data[0::2], data[1::2]))
    else:
        raise ValueError
    return data

def decode(text):
    """Manages function call and catches syntax errors in file.

    Args:
        text (str): Contents of file.

    Raises:
        SyntaxError: Invalid syntax in file

    Returns:
        (dict, list): Decoded file
    """    
    try:
        src = tokenize(text)
        data = decode_item(src.__next__, src.__next__())
        for token in src: # look for more tokens
            raise SyntaxError("trailing junk")
    except (AttributeError, ValueError, StopIteration):
        raise SyntaxError("Syntax error")

    return data


def main(file, path):
    """Main Function

    Args:
        file (str): Contents of the file.

    Raises:
        InvalidFileException: Raises if no substring 'pieces' is present(If no hash string is present)
    """    
    # Check for hash data:
    hashbreak = file.find(b'pieces')

    # If hash data is present:

    if hashbreak != -1:
        # Start index of hash
        hashstart = hashbreak + file[hashbreak:].find(b':') + 1

        #  length of hash data
        hashlength = int(file[hashbreak+6 : hashstart-1])

        # convert hash to hex string to make it readable
        hash = hashlib.sha1(file[hashstart:hashstart+hashlength]).hexdigest() 

        # Putting back data in proper format and convert byte -> str
        data = file[:hashbreak].decode('utf-8') + f'pieces{len(hash)}:' + hash + file[hashstart+hashlength:].decode('utf-8')

        torrent = decode(data)

        # prettify print!

        print(json.dumps(torrent, sort_keys=True, indent=4))

        # Save as json

        jsonpath = os.path.join(os.path.dirname(path), os.path.basename(path).split('.')[0]+'.json')

        with open(jsonpath, 'w') as outfile:
            json.dump(torrent, outfile, sort_keys=True, indent=4)
        
        print("File written to: " + jsonpath)
    
    # If hash data isn't present:

    else:
        # To be fixed
        raise InvalidFileException(message="Cannot read file")
    
    

if __name__ == "__main__":
    # This is where it starts
    if len(sys.argv) > 1:
         # If path is sent as an arguement
        path = sys.argv[1]
    else: 
        # If path is not sent as an arguement
        path = input("Complete File path: ")
    
    if path.split('.')[-1] == 'torrent' and os.path.exists(path):
        # If valid file exists in the path
        file = open(path, 'rb').read()
    else:
        # If valid file doesn't exist in the path
        raise InvalidFileException()
    
    # Main Function:
    main(file, path)

   