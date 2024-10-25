# test search blank

import re

# blank '' is always found in all strings
if re.search('', 'test'):
    print('found blank in string')