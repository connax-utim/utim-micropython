# Utim/Uhost setting
class Config(object):
    def __init__(self):
        self.uhost_name = '74657374'
        self.utim_name = '7574696d'
        self.mqtt = {'host': '192.168.0.12',
                     'user': 'test',
                     'pass': 'test',
                     'reconnect_time': 60}
        self.protocol = 'mqtt'
