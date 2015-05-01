Websocket based LG API
======================
Documentation of the websocket based API that modern LG TVs seem to use.

The documentation is based on network traces from the model `lg-50LB6500`_.

.. _lg-50LB6500: http://www.lg.com/cl/soporte-producto/lg-50LB6500

The protocol is asynchron (meaning that the client can send multible requests and the TV can answer to them in a different order or in one websocket packet).

* The client initiates a web socket connection to Port 3000/tcp (using Sec-WebSocket-Version: 13).

Client registers
----------------

* The client identifies itself to the TV (which program is used).

.. code:: json

  {
    "type": "register",
    "id": "1",
    "payload": {
      "client-key": "e240cff7deba158abe95a689f45e081b",
      "forcePairing": false,
      "manifest": {
        "appVersion": "1.1",
        "manifestVersion": 1,
        "permissions": [
          "LAUNCH",
          "TEST_OPEN",
          "TEST_PROTECTED",
          "CONTROL_AUDIO",
          "CONTROL_DISPLAY",
          "CONTROL_INPUT_JOYSTICK",
          "CONTROL_INPUT_MEDIA_RECORDING",
          "CONTROL_INPUT_MEDIA_PLAYBACK",
          "CONTROL_INPUT_TV",
          "CONTROL_POWER",
          "READ_APP_STATUS",
          "READ_CURRENT_CHANNEL",
          "READ_INPUT_DEVICE_LIST",
          "READ_NETWORK_STATE",
          "READ_RUNNING_APPS",
          "READ_TV_CHANNEL_LIST",
          "WRITE_NOTIFICATION_TOAST",
          "READ_POWER_STATE",
          "READ_COUNTRY_INFO"
        ],
        "signatures": [
          {
            "signature": "eyJhbGdvcml0aG0iOiJSU0EtU0hBMjU2Iiwia2V5SWQiOiJ0ZXN0LXNpZ25pbmctY2VydCIsInNpZ25hdHVyZVZlcnNpb24iOjF9.hrVRgjCwXVvE2OOSpDZ58hR+59aFNwYDyjQgKk3auukd7pcegmE2CzPCa0bJ0ZsRAcKkCTJrWo5iDzNhMBWRyaMOv5zWSrthlf7G128qvIlpMT0YNY+n/FaOHE73uLrS/g7swl3/qH/BGFG2Hu4RlL48eb3lLKqTt2xKHdCs6Cd4RMfJPYnzgvI4BNrFUKsjkcu+WD4OO2A27Pq1n50cMchmcaXadJhGrOqH5YmHdOCj5NSHzJYrsW0HPlpuAx/ECMeIZYDh6RMqaFM2DXzdKX9NmmyqzJ3o/0lkk/N97gfVRLW5hA29yeAwaCViZNCP8iC9aO0q9fQojoa7NQnAtw==",
            "signatureVersion": 1
          }
        ],
        "signed": {
          "appId": "com.lge.test",
          "created": "20140509",
          "localizedAppNames": {
            "": "LG Remote App",
            "ko-KR": "리모컨 앱",
            "zxx-XX": "ЛГ Rэмotэ AПП"
          },
          "localizedVendorNames": {
            "": "LG Electronics"
          },
          "permissions": [
            "TEST_SECURE",
            "CONTROL_INPUT_TEXT",
            "CONTROL_MOUSE_AND_KEYBOARD",
            "READ_INSTALLED_APPS",
            "READ_LGE_SDX",
            "READ_NOTIFICATIONS",
            "SEARCH",
            "WRITE_SETTINGS",
            "WRITE_NOTIFICATION_ALERT",
            "CONTROL_POWER",
            "READ_CURRENT_CHANNEL",
            "READ_RUNNING_APPS",
            "READ_UPDATE_INFO",
            "UPDATE_FROM_REMOTE_APP",
            "READ_LGE_TV_INPUT_EVENTS",
            "READ_TV_CURRENT_TIME"
          ],
          "serial": "2f930e2d2cfe083771f68e4fe7bb07",
          "vendorId": "com.lge"
        }
      },
      "pairingType": "PIN"
    }
  }

* The TV acknowledges.

.. code:: json

  {
    "id": "1",
    "type": "registered",
    "payload": {
      "client-key": "e240cff7deba158abe95a689f45e081b"
    }
  }

getCurrentSWInformation (ID 401)
--------------------------------

* Client requests current software version information from the TV.

.. code:: json

  {
    "id":       "401",
    "type":     "request",
    "payload":  "{}",
    "uri":      "ssap://com.webos.service.update/getCurrentSWInformation"
  }

* TV sends CurrentSWInformation.

.. code:: json

  {
    "id": "401",
    "type": "response",
    "payload": {
      "returnValue":     true,
      "product_name":    "webOS",
      "model_name":      "HE_DTV_WT1M_AFAAATAA",
      "sw_type":         "FIRMWARE",
      "major_ver":       "04",
      "minor_ver":       "34.24",
      "country":         "PE",
      "device_id":       "3c:cd:93:XX:XX:XX",
      "auth_flag":       "N",
      "ignore_disable":  "N",
      "eco_info":        "01",
      "config_key":      "00",
      "language_code":   "en-US"
    }
  }

getCurrentSWInformation (ID 90)
-------------------------------

* Client requests current software version information from the TV again (but ID 90).

.. code:: json

  {
    "id": "90",
    "type": "request",
    "payload": "{}",
    "uri": "ssap://com.webos.service.update/getCurrentSWInformation"
  }

* TV sends CurrentSWInformation again.

.. code:: json

  {
    "id": "90",
    "type": "response",
    "payload": {
      "returnValue":     true,
      "product_name":    "webOS",
      "model_name":      "HE_DTV_WT1M_AFAAATAA",
      "sw_type":         "FIRMWARE",
      "major_ver":       "04",
      "minor_ver":       "34.24",
      "country":         "PE",
      "device_id":       "3c:cd:93:XX:XX:XX",
      "auth_flag":       "N",
      "ignore_disable":  "N",
      "eco_info":        "01",
      "config_key":      "00",
      "language_code":   "en-US"
    }
  }

getSystemInfo
-------------

* Client requests System information.

.. code:: json

  {
    "id": "60",
    "type": "request",
    "uri": "ssap://system/getSystemInfo"
  }

* TV sends system information.

.. code:: json

  {
    "id": "60",
    "type": "response",
    "payload": {
      "features": {
        "3d": true,
        "dvr": true
      },
      "receiverType":  "atsc",
      "modelName":     "50LB6500-SF",
      "returnValue":   true
    }
  }

getExternalInputList
--------------------

* Client subscribes to ExternalInputList.

.. code:: json

  {
    "id":    "37",
    "type":  "subscribe",
    "uri":   "ssap://tv/getExternalInputList"
  }

* TV answers to subscription.

.. code:: json

  {
    "id": "37",
    "type": "response",
    "payload": {
      "devices": [
        {
          "id": "AV_1",
          "label": "AV",
          "port": 1,
          "appId": "com.webos.app.externalinput.av1",
          "icon": "http://192.168.1.42:3000/resources/f182ff211eab238249ca1a240727cf8b51ec18df/av.png",
          "modified": false,
          "subList": [],
          "subCount": 0,
          "connected": false,
          "favorite": false
        },
        {
          "id": "COMP_1",
          "label": "Component",
          "port": 1,
          "appId": "com.webos.app.externalinput.component",
          "icon": "http://192.168.1.42:3000/resources/70f3fe8064eaafa8dec1cce81b9eb1f9ff7d5845/component.png",
          "modified": false,
          "subList": [],
          "subCount": 0,
          "connected": false,
          "favorite": false
        },
        {
          "id": "HDMI_1",
          "label": "FTV",
          "port": 1,
          "appId": "com.webos.app.hdmi1",
          "icon": "http://192.168.1.42:3000/resources/1262af55b830514002c22cc473c1b5d80f705e75/streamingbox.png",
          "modified": true,
          "subList": [
            {
              "id": "SIMPLINK",
              "uniqueId": 4,
              "cecpDevType": 4,
              "cecpDevId": 15,
              "cecpNewType": 9,
              "version": 0,
              "osdName": "Amazon FireTV"
            }
          ],
          "oneDepth": true,
          "subCount": 1,
          "connected": true,
          "favorite": true
        },
        {
          "id": "HDMI_2",
          "label": "Claro",
          "port": 2,
          "appId": "com.webos.app.hdmi2",
          "icon": "http://192.168.1.42:3000/resources/53b086fbd9ed11b08b2df157a4d2bd69519d6e54/settopbox.png",
          "modified": true,
          "spdProductDescription": "DCX-700",
          "spdVendorName": "MOTOROLA",
          "spdSourceDeviceInfo": "Digital STB",
          "subList": [],
          "subCount": 0,
          "connected": true,
          "favorite": true
        },
        {
          "id": "HDMI_3",
          "label": "HDMI3",
          "port": 3,
          "appId": "com.webos.app.hdmi3",
          "icon": "http://192.168.1.42:3000/resources/1917fddf7e79c9c75746f016fe284e5d86f8e4c6/HDMI_3.png",
          "modified": false,
          "subList": [],
          "subCount": 0,
          "connected": false,
          "favorite": false
        }
      ],
      "returnValue": true
    }
  }

listInterestingEvents
---------------------

* TV acknowledges subscription.

.. code:: json

  {
    "id": "99",
    "type": "subscribe",
    "payload": "{\"subscribe\":true}",
    "uri": "ssap://com.webos.service.tv.keymanager/listInterestingEvents"
  }

* TV to client.

.. code:: json

  {
    "id": "99",
    "type": "response",
    "payload": {
      "returnValue": true,
      "events": [
        {
          "name": "keyEvent",
          "devices": [
            "remoteControl"
          ],
          "mask": [
            "arrow",
            "selection",
            "color",
            "playback",
            "goto",
            "back",
            "exit",
            "cec"
          ]
        }
      ]
    }
  }

getCurrentTime
--------------

* Client requests time from TV.

.. code:: json

  {
    "id": "102",
    "type": "subscribe",
    "uri": "ssap://com.webos.service.tv.time/getCurrentTime"
  }

* TV answers with the current time.

.. code:: json

  {
    "id": "102",
    "type": "response",
    "payload": {
      "returnValue": true,
      "time": {
        "year":    2015,
        "month":   1,
        "day":     25,
        "hour":    17,
        "minute":  47,
        "second":  7
      }
    }
  }

getChannelCurrentProgramInfo
----------------------------

* Client requests channel program information.

.. code:: json

  {
    "id": "101",
    "type": "request",
    "uri": "ssap://tv/getChannelCurrentProgramInfo"
  }

* TV returns error for channel program information.

.. code:: json

  {
    "id": "101",
    "type": "error",
    "error": "500 Application error",
    "payload": {
      "returnValue": false,
      "errorCode": -1000,
      "errorText": "no such channel"
    }
  }

getMute
-------

* Client queries mute state.

.. code:: json

  {
    "id": "15",
    "type": "subscribe",
    "uri": "ssap://audio/getMute"
  }

* TV returns mute state.

.. code:: json

  {
    "type": "response",
    "id": "15",
    "payload": {
      "mute": false,
      "returnValue": true
    }
  }

get3DStatus
-----------

* Client requests 3D status.

.. code:: json

  {
    "id": "41",
    "type": "subscribe",
    "payload": "{\"subscribe\":true}",
    "uri": "ssap://com.webos.service.tv.display/get3DStatus"
  }

* TV answers to 3D status.

.. code:: json

  {
    "type": "response",
    "id": "41",
    "payload": {
      "returnValue": true,
      "status3D": {
        "status": false,
        "pattern": "2d"
      }
    }
  }

getForegroundAppInfo
--------------------

* Client requests AppInfo.

.. code:: json

  {
    "id": "44",
    "type": "subscribe",
    "uri": "ssap://com.webos.applicationManager/getForegroundAppInfo"
  }

* TV returns AppInfo.

.. code:: json

  {
    "type": "response",
    "id": "44",
    "payload": {
      "appId":        "com.webos.app.hdmi1",
      "subscribed":   true,
      "returnValue":  true,
      "windowId":     "",
      "processId":    "1001"
    }
  }

registerRemoteKeyboard
----------------------

* Client registers remote keyboard :)

.. code:: json

  {
    "id": "50",
    "type": "subscribe",
    "uri": "ssap://com.webos.service.ime/registerRemoteKeyboard"
  }

* TV acknowledges remote keyboard subscription.

.. code:: json

  {
    "type": "response",
    "id": "50",
    "payload": {
      "subscribed": true
    }
  }

getPointerInputSocket
---------------------

* Client requests pointer input socket.

.. code:: json

  {
    "id": "100",
    "type": "request",
    "uri": "ssap://com.webos.service.networkinput/getPointerInputSocket"
  }

* TV returns pointer input socket.

.. code:: json

  {
    "type": "response",
    "id": "100",
    "payload": {
      "socketPath": "ws://192.168.1.42:3000/resources/3a85dcf82346495524edc6918c62975/netinput.pointer.sock",
      "returnValue": true
    }
  }
