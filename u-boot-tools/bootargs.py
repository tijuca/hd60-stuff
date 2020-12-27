#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Silly script to allow experiment with creating a crc32-checked file for the Mutant HD60 receiver

# SPDX-License-Identifier: MIT
# (C) Copyright 2020, written by Carsten Juttner <carjay@gmx.net>

#
#
# Examples:
#
# Decode bootargs.bin to bootargs.txt:
#   ./bootargs.py -d recovery/bootargs.bin -o bootargs.txt
#
# (Re)Encode bootargs.txt to bootargs_new.bin:
#   ./bootargs.py -e bootargs.txt -o bootargs_new.bin


import argparse
import struct
import binascii

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--decodefile", type=str, help="dump the contents of a bootargs.bin. Parameter is the bootargs.bin filename")
    parser.add_argument("-o", "--outputfile", type=str, help="file to write the decoded/encoded data to")
    parser.add_argument("-e", "--encodefile", type=str, help="file containing the bootargs input (as newline separated lines)")
    parser.add_argument("-p", "--padsize", type=str, help="size to pad the bootargs file to (default is 65536 bytes)")

    args = parser.parse_args()

    padsize = 0x10000
    if args.padsize:
        padsize = int(args.padsize)

    if args.decodefile and args.encodefile:
        print("Error: using both --decodefile and --encodefile at the same time is not supported")
        return

    if args.decodefile:
        if not args.outputfile:
            print("Error: -o,--outputfile option is missing but is required for --decodefile option")
            return
        try:
            with open(args.decodefile, 'rb') as fh:
                buffer = fh.read()
                print(f"Info: Read {len(buffer)} bytes")
                file_crc, = struct.unpack('<I', buffer[0:4])
                payload = buffer[4:65536]
                calculated_crc = binascii.crc32(payload)
                if file_crc == calculated_crc:
                    print(f"Info: Checksum {file_crc:x} matches")
                    with open(args.outputfile, 'w') as fw:
                        # remove all trailing zeroes
                        lines = [l.strip(b'\x00') for l in payload.split(b'\x00')]
                        # dump to file
                        writtencount = 0
                        for l in lines:
                            if not l:
                                continue # filter out empty lines but I don't think they should exist (and not sure if uboot would even support this)
                            # assume utf8
                            fw.write(l.decode('utf8') + '\n')
                            writtencount += 1
                        print(f"Info: Wrote {writtencount} lines to \"{args.outputfile}\"")

                else:
                    print(f"Warning: checksum mismatch file {file_crc:x}, calculated {calculated_crc:x}")
        except Exception as exc:
            print(f"Error decoding file: {str(exc)}")

    if args.encodefile:
        if not args.outputfile:
            print("Error: -o,--outputfile option is missing but is required for --encodefile option")
            return
        try:
            with open(args.encodefile, 'r') as fh:
                # drop all lines which are empty and just have a CR (\n)
                lines2 = [line.strip() for line in fh if line.strip()]
                line_list = []
                count = len(lines2)
                print(f"Info: Read {count} lines from input file.\n")
                for i in range(0, count):
                    # ignore all lines that start with '#', they are meant comments
                    if lines2[i].startswith('#'):
                        print('Info: Line {:2d} skipped (data was \'{}\')'.format(i + 1, lines2[i]))
                    else:
                        line_list.append(lines2[i])

                reencoded_lines = [ l.strip().encode('utf8') for l in line_list ]
                output = b'\x00'.join(reencoded_lines)

                if len(output) > (padsize - 4): # needs to include the crc32
                    print(f"Error: file too big to fit in {padsize} bytes, requires {len(output)+4}")
                    return

                output += b'\x00' * (padsize - 4 - len(output))
                crc = binascii.crc32(output)
                crc_bin = struct.pack('<I', crc)
                print(f"Info: Calculated checkout {crc:x}")
                output = crc_bin + output
                with open(args.outputfile, 'wb') as fw:
                    fw.write(output)
                print(f"Info: Successfully wrote file \"{args.outputfile}\"")
        except Exception as exc:
            print(f"Error encoding file: {str(exc)}")



try:
    main()
except KeyboardInterrupt:
    pass

