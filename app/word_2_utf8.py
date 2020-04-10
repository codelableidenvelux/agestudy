import io
import sys
"""
This script reads a file from one,  transforms and writes it into another encoding'
Takes 4 cli arguments
1: file to be transformed
2: encoding of that file
3: name of new file
4: encoding of new file
example:
python3 word_2_utf8.py templates/automatic_welcome.htm 1251 templates/automatic_welcome_encoded.htm utf-8
"""

html_file_r  = open(sys.argv[1], "r",encoding=sys.argv[2])
html_file = html_file_r.read()

html_file_w  = open(sys.argv[3], "w",encoding=sys.argv[4])
html_file_w.write(html_file)
