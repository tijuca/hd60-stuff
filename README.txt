+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+ Important and some non important notes about HD60 stuff +
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

1. HowTo to build the kernel
############################

You need some packages to cross build the kernel and modules etc. In case
you want to build the kernel native an any armhf (aka ARMv7) based system
you should drop the package 'crossbuild-essential-armhf' from the list of
packages to install.

 sudo apt install build-essential bison flex crossbuild-essential-armhf

Jump into the folder which contains the kernel. Make a copy of the predefined
kernel configuration.

 cd kernel
 cp hd60-defconfig .config

And finally build the binary things.

 make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- zImage dtbs modules -j4

Some more collected things around kernel image build for armhf based devices
can be found here:

https://github.com/umiddelb/armhf/wiki/How-To-compile-a-custom-Linux-kernel-for-your-ARM-device

The various patches added to the original kernel source and also the kernel
configuration file are taken from:

https://github.com/neutrino-hd/meta-hisilicon

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

2. U-Boot tools and things to know
##################################

The used U-Boot on the Mutant HD60 receiver is searching for a file
'bootargs.bin' on a USB device and in case this file is found it will
interpreted it's content and execute afterwards. That specific file is
basically a classical *.scr U-Boot script which is compiled into a file with
a 4 Byte long CRC32 header and a fixed length of 64kB.

To use the possibility to control the booting process through the file
'bootargs.bin' you need to take a about the hard requirements (CRC32 header
and max length of 64kB).

The folder u-boot-tool is holding a file bootargs.py which can decode
existing 'bootargs-bin' files but also create new files named bootargs.bin.

$ ./bootargs.py -h
usage: bootargs.py [-h] [-d DECODEFILE] [-o OUTPUTFILE] [-e ENCODEFILE] [-p PADSIZE]

optional arguments:
  -h, --help            show this help message and exit
  -d DECODEFILE, --decodefile DECODEFILE
                        dump the contents of a bootargs.bin. Parameter is the bootargs.bin filename
  -o OUTPUTFILE, --outputfile OUTPUTFILE
                        file to write the decoded/encoded data to
  -e ENCODEFILE, --encodefile ENCODEFILE
                        file containing the bootargs input (as newline separated lines)
  -p PADSIZE, --padsize PADSIZE
                        size to pad the bootargs file to (default is 65536 bytes)

