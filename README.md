# lgcommander.py
lgcommander.py is a Python script for controlling your Smart Lg TV with your PC.
It can be used for gaining access to hidden menus and modes.

## Supported models
Lg has released two TV remote control apps for android smartphones in Google Play app store; each with a list of supported models. One for 2012 models and the other for some earlier models. If your TV is not on those lists, it may not be controllable through a network connection and this script may not work for you.

## Requirements
A PC, with Python 3.x installed, connected to the same network as your Lg TV.

## Usage

See the available options with: `./lgcommander.py --help` or `python3 lgcommander.py --help`

    usage: lgcommander.py [-h] [-V] [-H HOST] [-p PORT] [-P {roap,hdcp}]
                          [-k PAIRING_KEY] [-c COMMAND]

    Control your Smart Lg TV with your PC

    optional arguments:
      -h, --help            show this help message and exit
      -V, --version         show program's version number and exit
      -H HOST, --host HOST  IP address or FQDN of device. Use the special value
                            "scan" for a multicast request for TVs in your LAN.
                            "scan" will also be used if this parameter was
                            omitted.
      -p PORT, --port PORT  TCP port (default is 8080).
      -P {roap,hdcp}, --protocol {roap,hdcp}
                            Protocol to use. Currently ROAP and HDCP are
                            supported. Default is to auto detect the correct one.
      -k PAIRING_KEY, --pairing-key PAIRING_KEY
                            Pairing key of your TV. This key is shown on request
                            on the screen and does only change if you factory
                            reset your TV.
      -c COMMAND, --command COMMAND
                            Send just a single command and exit.

## Some useful codes:

* for EZ_ADJUST menu enter 255
* for IN START menu enter 251
* for Installation menu enter 207
* for POWER_ONLY mode enter 254

*Warning*: Do not enter 254 if you do not know what POWER_ONLY mode is. You can find additional information about menus and modes here: <http://openlgtv.org.ru>

## Problem with latest LG firmware:
If you upgrade your TV firmware to 05.12.05 or later, "Tool Option 3" may be greyed out and you may not be able to make changes.  Please e-mail me if you have a solution to this problem (other than not upgrading).

### "Quinny" says:
> Thanks for LG Commander!
> I've just managed to sort out the Options3 greyed out issue.
> Follow the instructions here: http://www.avforums.com/forums/lg-forum/1651400-official-lg-lw550t-3d-led-thread-part-9-a.html

## Windows users:
You can avoid the black console window if you change the "py" file extension to "pyw".

## Newer LG Smart TV (year 2012) models:

### Benke Tamás:
> I wanted to use your lgcommander script, but I realized that its not working with lg 2012 smart tv series. I made some changes, now its working with the new series, but lg changed the keycodes too. Now, there are keycodes above 255 and ez-adjust, in-start code changed too, but I dont know them yet. I attached my version, if you want to improve yours.

* Benke's version of the script was added as lg_2012_commander.py.
* [ypid](https://github.com/ypid) combined the script into lgcommander.py (use `./lgcommander.py -P roap`).

### Ajay Ramaswamy:
> Hi,
>
> Thanks for your lgcommander script. I was playing around with my 2012 55LM6200
> TV and LG has provided a Android App Smart TV which provides a remote control
> app.
>
> I ran that app thru unzip, dex2class and JD-GUI and found the file
> com/lge/tv/remoteapps/Base/RemoteKeyIndex.class contains these key mappings
>
>
>         KEY_IDX_3D=400;
>         KEY_IDX_ARROW_DOWN=2;
>         KEY_IDX_ARROW_LEFT=3;
>         KEY_IDX_ARROW_RIGHT=4;
>         KEY_IDX_ARROW_UP=1;
>         KEY_IDX_BACK=23;
>         KEY_IDX_BLUE=29;
>         KEY_IDX_BTN_1=5;
>         KEY_IDX_BTN_2=6;
>         KEY_IDX_BTN_3=7;
>         KEY_IDX_BTN_4=8;
>         KEY_IDX_CH_DOWN=28;
>         KEY_IDX_CH_UP=27;
>         KEY_IDX_ENTER=20;
>         KEY_IDX_EXIT=412;
>         KEY_IDX_EXTERNAL_INPUT=47;
>         KEY_IDX_GREEN=30;
>         KEY_IDX_HOME=21;
>         KEY_IDX_MUTE=26;
>         KEY_IDX_MYAPPS=417;
>         KEY_IDX_NETCAST=408;
>         KEY_IDX_PAUSE=34;
>         KEY_IDX_PLAY=33;
>         KEY_IDX_POWER_OFF=1;
>         KEY_IDX_PREV_CHANNEL=403;
>         KEY_IDX_RED=31;
>         KEY_IDX_STOP=35;
>         KEY_IDX_VOL_DOWN=25;
>         KEY_IDX_VOL_UP=24;
>         KEY_IDX_YELLOW=32;
>
> I have tried all these codes on my TV and they work OK
>
> I hope you find this useful and someone else can test and confirm, and speed up
> the search for the Service Menu codes.
>
> Thanks & best regards
>
> Ajay

## This software was developed with inspiration and/or information taken from:

* <http://python.org>


* <http://openlgtv.org.ru>


* An application written in ruby where you can find a comprehensive list of command codes:
<https://github.com/dreamcat4/lgremote>
