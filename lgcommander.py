#!/usr/bin/env python3
# encoding: utf-8

# Todo:
# Use the same TCP connection.

__version__ = '0.5'

import re
import logging
import socket

import xml.etree.ElementTree as etree
import http.client
from tkinter import Tk, Toplevel, Entry, Button, Label

class MyDialog:

    def __init__(self, parent, dialog_msg):
        self.user_string = None

        top = self.top = Toplevel(parent)
        Label(top, text=dialog_msg, justify='left').pack()
        self.e = Entry(top)
        self.e.pack(padx=5)
        self.e.focus_set()
        b = Button(top, text='Ok', command=self.ok)
        b.pack(pady=5)
        top.bind('<Return>', self.ok)
        top.title(u"Lg Commander")
        top.geometry("410x280+10+10")

    def ok(self, dummy=None):
        self.user_string = self.e.get()
        self.top.destroy()

class KeyInputError(Exception):
    pass

class LgRemote:

    _xml_version_string = '<?xml version="1.0" encoding="utf-8"?>'
    _headers = {'Content-Type': 'application/atom+xml'}
    _highest_key_input_for_protocol = {
        'hdcp': 255,
        'roap': 1024,
    }

    def __init__(
            self,
            host=None,
            port=8080,
            protocol=None
    ):

        self.port = port
        try:
            port = int(self.port)
        except ValueError:
            # if not self.port == 'reported':
            raise Exception(u"Port is not a number: {}".format(self.port))
        else:
            self.port = port

        self.host = host
        if not self.host:
            self.getip()
        self._protocol = protocol
        if not self._protocol:
            self.auto_detect_accepted_protocol()
        self._pairing_key = None
        self._session_id = None

    def getip(self):
        if self.host:
            return self.host
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
        sock.sendto(bytestoXmit, ('239.255.255.250', 1900))
        while not found and i <= 5 and gotstr == 'notyet':
            try:
                gotbytes, addressport = sock.recvfrom(512)
                gotstr = gotbytes.decode()
            except:
                i += 1
                sock.sendto(bytestoXmit, ('239.255.255.250', 1900))
            if re.search('LG', gotstr):
                logging.debug(u"Returned: {}".format(gotstr))
                self.host, port = addressport
                logging.debug(u"Found device: {}".format(self.host))
                # (SSDP source port {}/udp)
                # Who cares …

                found = True
            else:
                gotstr = 'notyet'
            i += 1
        sock.close()
        if not found:
            raise socket.error(u"Lg TV not found.")
        logging.info(u"Using device: {} over transport protocol: {}/tcp".format(self.host, self.port))
        return self.host

    def auto_detect_accepted_protocol(self):
        req_key_xml_string = self._xml_version_string + '<auth><type>AuthKeyReq</type></auth>'
        logging.debug(u"Detecting accepted protocol.")
        if self._doesServiceExist(3000):
            raise Exception(u"Protocol not supported. See https://github.com/ypid/lgcommander/issues/1")
        for protocol in self._highest_key_input_for_protocol:
            logging.debug(u"Testing protocol: {}".format(protocol))
            conn = http.client.HTTPConnection(self.host, port=self.port)
            conn.request(
                "POST",
                "/{}/api/auth".format(protocol),
                req_key_xml_string,
                headers=self._headers)
            http_response = conn.getresponse()
            logging.debug(u"Got response: {}".format(http_response.reason))
            if http_response.reason == 'OK':
                self._protocol = protocol
                logging.debug(u"Using protocol: {}".format(self._protocol))
                return self._protocol
        raise Exception(u"No accepted protocol found.")

    def display_key_on_screen(self):
        conn = http.client.HTTPConnection(self.host, port=self.port)
        req_key_xml_string = self._xml_version_string + '<auth><type>AuthKeyReq</type></auth>'
        logging.debug(u"Request device to show key on screen.")
        conn.request(
            'POST',
            '/{}/api/auth'.format(self._protocol),
            req_key_xml_string,
            headers=self._headers)
        http_response = conn.getresponse()
        logging.debug(u"Device response was: {}".format(http_response.reason))
        if http_response.reason != "OK":
            raise Exception(u"Network error: {}".format(http_response.reason))
        return http_response.reason

    def get_session_id(self, paring_key):
        if not paring_key:
            return None

        self._pairing_key = paring_key
        logging.debug(u"Trying paring key: {}".format(self._pairing_key))
        pair_cmd_xml_string = self._xml_version_string \
            + '<auth><type>AuthReq</type><value>' \
            + self._pairing_key + '</value></auth>'
        conn = http.client.HTTPConnection(self.host, port=self.port)
        conn.request(
            'POST',
            '/{}/api/auth'.format(self._protocol),
            pair_cmd_xml_string,
            headers=self._headers)
        http_response = conn.getresponse()
        if http_response.reason != 'OK':
            return None
        tree = etree.XML(http_response.read())
        self._session_id = tree.find('session').text
        logging.debug(u"Session ID is {}".format(self._session_id))
        if len(self._session_id) < 8:
            raise Exception(u"Could not get Session Id: {}".format(self._session_id))
        return self._session_id

    def handle_key_input(self, cmdcode):
        highest_key_input = self._highest_key_input_for_protocol[self._protocol]
        try:
            if 0 > int(cmdcode) or int(cmdcode) > highest_key_input:
                raise KeyInputError(u"Key input {} is not supported.".format(cmdcode))
        except ValueError:
            raise KeyInputError(u"Key input {} is not a number".format(cmdcode))
        if not self._session_id:
            raise Exception(u"No valid session key available.")

        command_url_for_protocol = {
            'hdcp': '/{}/api/dtv_wifirc'.format(self._protocol),
            'roap': '/{}/api/command'.format(self._protocol),
        }

        logging.debug(u"Executing command: {}".format(cmdcode))
        key_input_xml_string = self._xml_version_string + '<command><session>' \
            + self._session_id \
            + '</session><type>HandleKeyInput</type><value>' \
            + cmdcode \
            + '</value></command>'
        conn = http.client.HTTPConnection(self.host, port=self.port)
        conn.request(
            'POST',
            command_url_for_protocol[self._protocol],
            key_input_xml_string,
            headers=self._headers)
        return conn.getresponse()

    def _doesServiceExist(self, port):
        """
        http://stackoverflow.com/a/14118271
        """

        # captive_dns_addr = None
        # host_addr = None

        # try:
        #     captive_dns_addr = socket.gethostbyname(self.host)
        # except:
        #     pass

        try:
            logging.debug(u"Trying to connect to port {}/tcp".format(port))

            # host_addr = socket.gethostbyname(self.host)
            # if (captive_dns_addr == host_addr):
            #     return False

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((self.host, port))
            s.close()
        except:
            return False

        return True


def main():  # {{{
    """Execute module in command line mode."""

    def get_pairing_key_from_user(lg_remote):
        lg_remote.display_key_on_screen()
        root = Tk()
        root.withdraw()
        dialog_msg = u"Please enter the pairing key\nyou see on your TV screen\n"
        dialog = MyDialog(root, dialog_msg)
        root.wait_window(dialog.top)
        session_id = dialog.user_string
        dialog.top.destroy()
        return session_id

    args = ArgumentParser(
        description=u"Control your Smart Lg TV with your PC",
    )
    args.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s {version}'.format(version=__version__)
    )
    args.add_argument(
        '-H',
        '--host',
        default='scan',
        help=u"IP address or FQDN of device."
        + u" Use the special value \"scan\" for a multicast request for TVs in your LAN."
        + u" \"scan\" will also be used if this parameter was omitted."
    )
    args.add_argument(
        '-p',
        '--port',
        default='8080',
        help=u"TCP port (default is 8080)."
    )
    args.add_argument(
        '-P',
        '--protocol',
        choices=['roap', 'hdcp'],
        default=None,
        help=u"Protocol to use."
        + u" Currently ROAP and HDCP are supported."
        + u" Default is to auto detect the correct one.",
    )
    args.add_argument(
        '-k',
        '--pairing-key',
        help=u"Pairing key of your TV."
        + u" This key is shown on request on the screen"
        + u" and does only change if you factory reset your TV."
    )
    args.add_argument(
        '-c',
        '--command',
        help=u"Send just a single command and exit."
    )
    user_parms = args.parse_args()

    logging.basicConfig(
        format=u'# %(levelname)s: %(message)s',
        level=logging.DEBUG,
        # level=logging.INFO,
    )

    try:
        lg_remote = LgRemote(
            host=None if user_parms.host == 'scan' else user_parms.host,
            port=user_parms.port,
            protocol=user_parms.protocol)
    except socket.error as error:
        raise SystemExit(error)

    if user_parms.pairing_key:
        logging.debug(u"Pairing key from user {}".format(user_parms.pairing_key))
        lg_remote.get_session_id(user_parms.pairing_key)
    while not lg_remote._session_id:
        logging.debug(u"No valid pairing key from user. Asking user …")
        lg_remote.get_session_id(get_pairing_key_from_user(lg_remote))

    dialog_msg = u"Session ID: " + str(lg_remote._session_id) + "\n"
    dialog_msg += u"Paring key: " + str(lg_remote._pairing_key) + "\n"
    dialog_msg += u"Success in establishing command session\n"
    dialog_msg += u"=" * 28 + "\n"
    dialog_msg += u"Enter command code i.e. a number between 0 and 255\n"
    dialog_msg += u"Enter a number greater than 255 to quit.\n"
    dialog_msg += u"Some useful codes:\n"
    dialog_msg += u"for EZ_ADJUST     menu enter   255 \n"
    dialog_msg += u"for IN START        menu enter   251 \n"
    dialog_msg += u"for Installation     menu enter   207 \n"
    dialog_msg += u"for POWER_ONLY mode enter   254 \n"
    dialog_msg += u"Warning: do not enter 254 if you \n"
    dialog_msg += u"do not know what POWER_ONLY mode is. "

    if user_parms.command:
        lg_remote.handle_key_input(user_parms.command)
        raise SystemExit()

    while True:
        root = Tk()
        root.withdraw()
        dialog = MyDialog(root, dialog_msg)
        root.wait_window(dialog.top)
        try:
            lg_remote.handle_key_input(dialog.user_string)
        except KeyInputError:
            logging.debug(u"Terminate on user requested.")
            break

if __name__ == '__main__':
    from argparse import ArgumentParser

    main()
# }}}
