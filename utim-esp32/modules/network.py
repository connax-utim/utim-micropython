import network
ssid = "connax"
password = "1berezka"
sta_if = network.WLAN(network.STA_IF);
sta_if.active(True)
sta_if.scan()
sta_if.connect(ssid, password)
sta_if.isconnected()
