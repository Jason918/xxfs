#!/usr/bin/python
#coding=utf-8

import sys
import xxfslib

op_dict = {
    "add": xxfslib.add,
    "append":xxfslib.append,
    "delete":xxfslib.delete,
    "get":xxfslib.get,
    "exist":xxfslib.exist,
    "sizeof":xxfslib.sizeof,
    "mkdir":xxfslib.mkdir,
    "rmdir":xxfslib.rmdir,
    "ls":xxfslib.ls
}
if __name__ == "__main__":
    argv = sys.argv
    # print argv
    if len(argv) < 2:
        print ''' usage: xxfs operation targets...
        [File Operation]
        xxfs add local_file remote_path
        xxfs append remote_file local_file_to_append
        xxfs delete remote_file
        xxfs get remote_file local_path
        xxfs exist remote_file
        xxfs sizeof remote_file

        [Directory Operation]
        xxfs mkdir directory
        xxfs rmdir directory
        xxfs ls directory
        '''
        exit(0)
    op = argv[1]
    if op_dict.has_key(op):
        op_dict[op](argv[2:])
    else:
        print "invalid operation"
