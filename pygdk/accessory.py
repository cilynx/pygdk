class Accessory:
    def __init__(self, name, config):
        # print(f"Accessory.__init__({config})")
        self.name = name
        self.before = config.get('Auto').lower() == 'before'
        self.after = config.get('Auto').lower() == 'after'
        self.tasmota = Tasmota(config.get('Tasmota', None)) if config.get('Tasmota', None) else None
        self.wemo = WeMo(config.get('WeMo', None)) if config.get('WeMo', None) else None

    def power_on(self):
        if self.tasmota:
            self.tasmota.on()
        elif self.wemo:
            self.wemo.on()
        else:
            raise ValueError('No smart plug found.  Please check your `Accessary` configuration')

    def power_off(self):
        if self.tasmota:
            self.tasmota.off()
        elif self.wemo:
            self.wemo.off()
        else:
            raise ValueError('No smart plug found.  Please check your `Accessory` configuration')


class Tasmota:

    def __init__(self, config):
        # print("Tasmota.__init__()")
        self.host = config[0]
        self.id = ''
        if len(config) == 2:
            self.id = config[1]
        elif len(config) != 1:
            raise ValueError('Tasmota configuration error.  See https://github.com/cilynx/pygdk#machine-configuration for assistance.')

    def on(self):
        import requests
        # print("Tasmota.on()")
        return requests.get(f"http://{self.host}/cm?cmnd=Power{self.id}%20On")

    def off(self):
        import requests
        # print("Tasmota.off()")
        return requests.get(f"http://{self.host}/cm?cmnd=Power{self.id}%20Off")

    @property
    def is_on(self):
        import json
        import requests
        response = requests.get(f"http://{self.host}/cm?cmnd=Power{self.id}")
        return(json.loads(response.text)[f"POWER{self.id}"] == "ON")


class WeMo:

    def __init__(self, config):
        # print("WeMo.__init__()")
        self.host, self.id = config

    def on(self):
        import pywemo
        # print("WeMo.on()")
        if 'obj' not in self:
            self.obj = pywemo.discovery.device_from_description(f"http://{self.host}:49153/setup.xml")
        return self.obj.on()

    def off(self):
        import pywemo
        # print("WeMo.off()")
        if 'obj' not in self:
            self.obj = pywemo.discovery.device_from_description(f"http://{self.host}:49153/setup.xml")
        return self.obj.off()
