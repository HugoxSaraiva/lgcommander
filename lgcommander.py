#!/usr/bin/env python3
# encoding: utf-8

# Todo:
# Use the same TCP connection.

__version__ = '0.5.1'

import requests
import xml.etree.ElementTree as Et
import socket
import sys
import logging


class LgRemote:
    _headers = {'Content-Type': 'application/atom+xml'}
    _highest_key_input_for_protocol = {
        'hdcp': 255,
        'roap': 1024,
    }

    def __init__(self, host=None, port=8080, protocol=None, pairing_key=None):
        if str(port).isdigit():
            self.port = port
        else:
            raise ValueError("Port is not a valid number: {}".format(port))
        self.host = host if host else self.get_ip()
        self.protocol = protocol if protocol else self._get_accepted_protocol()
        self.pairing_key = pairing_key
        self.session_id = self.get_session_id(pairing_key) if pairing_key else None

    @staticmethod
    def _dict_to_xml(tag, dictionary):
        element = Et.Element(tag)
        for key, val in dictionary.items():
            # create an Element class object
            child = Et.Element(key)
            child.text = str(val)
            element.append(child)
        return Et.tostring(element, encoding="unicode", method="xml")

    @staticmethod
    def get_ip():
        # Finds the ip address of a LG TV connected to the network
        ssdp_discover = 'M-SEARCH * HTTP/1.1' + '\r\n' + \
                        'HOST: 239.255.255.250:1900' + '\r\n' + \
                        'MAN: "ssdp:discover"' + '\r\n' + \
                        'MX: 2' + '\r\n' + \
                        'ST: urn:schemas-upnp-org:device:MediaRenderer:1' + '\r\n' + '\r\n'
        broadcast_ip = '239.255.255.250'
        broadcast_port = 1900
        ipaddress = None

        # Set up TCP socket to find devices on network
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.settimeout(3)
        try:
            while True:
                sock.sendto(ssdp_discover.encode(), (broadcast_ip, broadcast_port))
                data, address = sock.recvfrom(1024)
                string_received = data.decode()
                if "LG" in string_received:
                    logging.debug("Received string :\n{}".format(string_received))
                    ipaddress, _ = address
                    logging.debug("Found device ip: {}".format(ipaddress))
                    break
        except socket.timeout:
            pass
        sock.close()
        if not ipaddress:
            raise socket.error("Lg TV not found")
        logging.info("Using device ip: {}".format(ipaddress))
        return ipaddress

    def _get_accepted_protocol(self):
        # Connects to TV and requests it to display pairing key
        payload = {"type": "AuthKeyReq"}

        logging.debug("Detecting accepted protocol.")

        for protocol in self._highest_key_input_for_protocol:
            logging.debug("Testing protocol: {}".format(protocol))
            url = "http://{}:{}/{}/api/auth".format(self.host, self.port, protocol)
            res = requests.post(
                url,
                data=self._dict_to_xml('auth', payload),
                headers=self._headers
            )
            logging.debug("Got response: {}".format(res.reason))
            if res.reason == "OK":
                logging.debug("Using protocol: {}".format(protocol))
                return protocol
        raise Exception("No accepted protocol found.")

    def display_key(self):
        # Connects to TV and requests it to display pairing key
        url = "http://{}:{}/{}/api/auth".format(self.host, self.port, self.protocol)
        payload = {"type": "AuthKeyReq"}
        logging.debug("Requesting device to show key on screen...")
        res = requests.post(url, data=self._dict_to_xml('auth', payload), headers=self._headers)
        logging.debug("Response from {} was : {}".format(url, res.reason))
        if res.reason != "OK":
            raise Exception("Network error: {}".format(res.reason))
        return

    def get_session_id(self, paring_key):
        url = "http://{}:{}/{}/api/auth".format(self.host, self.port, self.protocol)
        payload = {
            "type": "AuthReq",
            "value": paring_key
        }
        logging.debug("Trying paring key: {}".format(paring_key))
        res = requests.post(url, data=self._dict_to_xml('auth', payload), headers=self._headers)
        logging.debug("Received response {}".format(res.reason))
        if res.reason != "OK":
            return None
        try:
            session_id = Et.XML(res.text).find('session').text
            if len(session_id) < 8:
                raise Exception("Could not get Session Id: {}".format(self.session_id))
            logging.debug("Session ID is {}".format(session_id))
        except AttributeError:
            return None
        return session_id

    def handle_key_command(self, command_code):
        # Check if code used is OK
        max_code = self._highest_key_input_for_protocol[self.protocol]
        if int(command_code) < 0 or int(command_code) > max_code:
            logging.debug("Key input {} is not supported.".format(command_code))
            return

        url_for_protocol = "dtv_wifirc" if self.protocol == "hdcp" else "command"
        url = "http://{}:{}/{}/api/{}".format(self.host, self.port, self.protocol, url_for_protocol)
        payload = {
            "session": self.session_id,
            "type": "HandleKeyInput",
            "value": command_code
        }
        res = requests.post(url, data=self._dict_to_xml('command', payload), headers=self._headers)
        return res.reason


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Control LG-TV over wifi.')
    parser.add_argument('-c', '--command', type=int, dest="command", help='Command to send to TV')
    parser.add_argument('-H', '--host', dest="host", default=None, help="IP address of device. "
                                             "If not set a multicast request will be made for TVs in your LAN.")
    parser.add_argument('-p', '--port', default='8080', help="TCP port (default is 8080).")
    parser.add_argument('-k', '--key', type=int, dest="key", default=None,
                        help='Pairing key used to connect to TV. Pairing key will be displayed on TV if not provided')
    parser.add_argument('-P', '--protocol', dest="protocol", choices=['roap', 'hdcp'], default=None,
                        help="Protocol to use. Currently ROAP and HDCP are supported."
                             " Default is to auto detect the correct one.")
    parser.add_argument('--debug', action='store_true', help='print debug messages')
    args = parser.parse_args()

    logging_level = logging.DEBUG if args.debug else logging.CRITICAL

    logging.basicConfig(
        format='# %(levelname)s: %(message)s',
        level=logging_level,
    )

    # Handle turning TV on if the device has cec-client installed and is connected to the TV through HDMI
    # if args.command == 0:
    #     from subprocess import call, PIPE
    #     logging.debug("Turning TV on")
    #     cmd = "echo 'on 0.0.0.0' | cec-client -s -d 1"
    #     call(cmd, shell=True, stdout=PIPE)
    #     sys.exit(0)

    lg_tv = LgRemote(args.host, args.port, args.protocol, args.key)

    if not lg_tv.pairing_key:
        logging.debug("No pairing key provided, proceeding to display it on screen")
        lg_tv.display_key()
        sys.exit(0)

    # Pairing key was given, proceeding to check if a session can be established
    if not lg_tv.session_id:
        logging.debug("Session id couldn't be established")
        lg_tv.display_key()
        sys.exit(1)

    if args.command:
        lg_tv.handle_key_command(args.command)

