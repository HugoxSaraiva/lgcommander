#!/usr/bin/env python3
# Todo:
# Use the same TCP connection.

__version__ = '0.4'

import re
import sys
import logging
import socket

import xml.etree.ElementTree as etree
import http.client
from tkinter import *

lgtv = {}
dialogMsg = ""
lgtv["pairingKey"] = "DDGWAF"

class MyDialog:

    def __init__(self, parent, dialogMsg):
        top = self.top = Toplevel(parent)
        Label(top, text=dialogMsg, justify="left").pack()
        self.e = Entry(top)
        self.e.pack(padx=5)
        self.e.focus_set()
        b = Button(top, text="Ok", command=self.ok)
        b.pack(pady=5)
        top.bind("<Return>", self.ok)
        top.title("Lg Commander")
        top.geometry("410x280+10+10")

    def ok(self, dummy=None):
        global result
        result = self.e.get()
        self.top.destroy()


class LgRemote:

    def __init__(
            self,
            ip_address,
            port=8080,
            protocol='hdcp'
    ):

        self.ip_address = ip_address
        self.port = port
        self._protocol = protocol
        self._session_id = None
        self._xml_version_string = '<?xml version="1.0" encoding="utf-8"?>'
        self._headers = {"Content-Type": "application/atom+xml"}

    def getip(self):
        strngtoXmit = 'M-SEARCH * HTTP/1.1' + '\r\n' + \
            'HOST: 239.255.255.250:1900' + '\r\n' + \
            'MAN: "ssdp:discover"' + '\r\n' + \
            'MX: 2' + '\r\n' + \
            'ST: urn:schemas-upnp-org:device:MediaRenderer:1' + \
            '\r\n' + '\r\n'

        bytestoXmit = strngtoXmit.encode()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3)
        found = False
        gotstr = 'notyet'
        i = 0
        ipaddress = None
        sock.sendto(bytestoXmit, ('239.255.255.250', 1900))
        while not found and i <= 5 and gotstr == 'notyet':
            try:
                gotbytes, addressport = sock.recvfrom(512)
                gotstr = gotbytes.decode()
            except:
                i += 1
                sock.sendto(bytestoXmit, ('239.255.255.250', 1900))
            if re.search('LG', gotstr):
                ipaddress, _ = addressport
                found = True
            else:
                gotstr = 'notyet'
            i += 1
        sock.close()
        if not found:
            sys.exit("Lg TV not found")
        return ipaddress

    def displayKey(self):
        conn = http.client.HTTPConnection(self.ip_address, port=self.port)
        req_key_xml_string = self._xml_version_string + 'auth><type>AuthKeyReq</type></auth>'
        conn.request(
            "POST",
            "/{}/api/auth".format(self._protocol),
            req_key_xml_string,
            headers=self._headers)
        http_response = conn.getresponse()
        if http_response.reason != "OK":
            raise Exception("Network error: {}".format(http_response.reason))
        return http_response.reason

    def get_session_id(self, paring_key):
        pair_cmd_xml_string = self._xml_version_string \
            + '<auth><type>AuthReq</type><value>' \
            + paring_key + "</value></auth>"
        conn = http.client.HTTPConnection(self.ip_address, port=self.port)
        conn.request(
            'POST',
            "/{}/api/auth".format(self._protocol),
            pair_cmd_xml_string,
            headers=self._headers)
        http_response = conn.getresponse()
        if http_response.reason != "OK":
            return None
        tree = etree.XML(http_response.read())
        self._session_id = tree.find('session').text
        logging.debug('Session ID is %s', self._session_id)
        return self._session_id

    def handleCommand(self, cmdcode):
        command_url_for_protocol = {
            'hdcp': '/{}/api/dtv_wifirc'.format(self._protocol),
            'roap': '/{}/api/command'.format(self._protocol),
        }
        key_input_xml_string = self._xml_version_string + '<command><session>' \
            + self._session_id \
            + "</session><type>HandleKeyInput</type><value>" \
            + cmdcode \
            + "</value></command>"
        conn = http.client.HTTPConnection(self.ip_address, port=self.port)
        conn.request(
            "POST",
            command_url_for_protocol[self._protocol],
            key_input_xml_string,
            headers=self._headers)
        return conn.getresponse()

def getPairingKey(lg_remote):
    lg_remote.displayKey()
    root = Tk()
    root.withdraw()
    dialogMsg = "Please enter the pairing key\nyou see on your TV screen\n"
    d = MyDialog(root, dialogMsg)
    root.wait_window(d.top)
    d.top.destroy()
    return result

def main():  # {{{
    """Execute module in command line mode."""

    args = ArgumentParser(
        description="Control your Smart Lg TV with your PC",
    )
    args.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s {version}'.format(version=__version__)
    )
    args.add_argument(
        'ip_address',
        help=u"raw test file file",
    )
    args.add_argument(
        '-p',
        '--port',
        help=u"TCP port (default is 8080)"
    )
    args.add_argument(
        '-P',
        '--protocol',
        choices=['roap', 'hdcp'],
        default='hdcp',
        help="Protocol to use."
        + " Currently ROSP and HDCP are supported. Default is HDCP.",
    )
    args.add_argument(
        '-k',
        '--pairing-key',
        help="Pairing key of your TV. This key is shown on request on the screen and does only change if you factory reset your TV."
    )
    args.add_argument(
        '-c',
        '--command',
        help="Send just a single command and exit."
    )
    user_parms = args.parse_args()

    logging.basicConfig(
        format='# %(levelname)s: %(message)s',
        level=logging.DEBUG,
        # level=logging.INFO,
    )

    lg_remote = LgRemote(user_parms.ip_address, protocol=user_parms.protocol)

    theSessionid = None
    if user_parms.pairing_key:
        logging.debug('Pairing key from user %s', user_parms.pairing_key)
        theSessionid = lg_remote.get_session_id(user_parms.pairing_key)
    while theSessionid is None:
        theSessionid = lg_remote.get_session_id(getPairingKey(lg_remote))

    if len(theSessionid) < 8:
        sys.exit("Could not get Session Id: " + theSessionid)

    lgtv["session"] = theSessionid
    dialogMsg = ""
    for lgkey in lgtv:
        dialogMsg += lgkey + ": " + lgtv[lgkey] + "\n"

    dialogMsg += "Success in establishing command session\n"
    dialogMsg += "=" * 28 + "\n"
    dialogMsg += "Enter command code i.e. a number between 0 and 255\n"
    dialogMsg += "Enter a number greater than 255 to quit.\n"
    dialogMsg += "Some useful codes:\n"
    dialogMsg += "for EZ_ADJUST     menu enter   255 \n"
    dialogMsg += "for IN START        menu enter   251 \n"
    dialogMsg += "for Installation     menu enter   207 \n"
    dialogMsg += "for POWER_ONLY mode enter   254 \n"
    dialogMsg += "Warning: do not enter 254 if you \n"
    dialogMsg += "do not know what POWER_ONLY mode is. "

    if user_parms.command:
        lg_remote.handleCommand(user_parms.command)
        sys.exit(0)

    result = "26"
    while int(result) <= 255:
        root = Tk()
        root.withdraw()
        d = MyDialog(root, dialogMsg)
        root.wait_window(d.top)
        lg_remote.handleCommand(result)

if __name__ == '__main__':
    from argparse import ArgumentParser

    main()
# }}}
