#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from pisi.actionsapi import shelltools
from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import get

WorkDir="%s-%s" % (get.srcNAME(), get.srcVERSION())

def setup():
    # Create nss.pc and nss-config dynamically
    shelltools.system("./generate-pc-config.sh")

def build():
    if get.ARCH() == "x86_64":
        shelltools.export("USE_64", "1")

    shelltools.export("BUILD_OPT", "1")
    shelltools.export("NSS_ENABLE_ECC", "1")
    shelltools.export("NSS_USE_SYSTEM_SQLITE", "1")
    shelltools.export("NSPR_INCLUDE_DIR", "`nspr-config --includedir`")
    shelltools.export("NSPR_LIB_DIR", "`nspr-config --libdir`")
    shelltools.export("XCFLAGS","%s -g -fno-strict-aliasing" % get.CFLAGS())

    # Use system zlib
    shelltools.export("PKG_CONFIG_ALLOW_SYSTEM_LIBS", "1")
    shelltools.export("PKG_CONFIG_ALLOW_SYSTEM_CFLAGS", "1")

    autotools.make("-C nss/coreconf -j1")
    autotools.make("-C nss/lib/dbm")
    autotools.make("-C nss -j1")

def install():
    for binary in ["certutil", "modutil", "pk12util", "signtool", "ssltap"]:
        pisitools.insinto("/usr/bin","dist/Linux*/bin/%s" % binary, sym=False)

    for lib in ["*.a","*.chk","*.so"]:
        pisitools.insinto("/usr/lib/nss","dist/Linux*/lib/%s" % lib, sym=False)

    # Headers
    for header in ["dist/private/nss/*.h","dist/public/nss/*.h"]:
        pisitools.insinto("/usr/include/nss", header, sym=False)

    # Drop executable bits from headers
    shelltools.chmod("%s/usr/include/nss/*.h" % get.installDIR(), mode=0644)

    # Install nss-config and nss.pc
    pisitools.insinto("/usr/lib/pkgconfig", "dist/pkgconfig/nss.pc")
    pisitools.insinto("/usr/bin", "dist/pkgconfig/nss-config")

    # create empty NSS database
    pisitools.dodir("/etc/pki/nssdb")
    shelltools.export("LD_LIBRARY_PATH", "%s/usr/lib/nss" % get.installDIR())
    shelltools.system("%s/usr/bin/modutil -force -dbdir \"sql:%s/etc/pki/nssdb\" -create" % (get.installDIR(), get.installDIR()))
    shelltools.chmod("%s/etc/pki/nssdb/*" % get.installDIR(), 0644)
    pisitools.dosed("%s/etc/pki/nssdb/*" % get.installDIR(), get.installDIR(), "")
