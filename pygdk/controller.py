from .accessory import Tasmota, WeMo, Accessory

class Controller:
    def __init__(self, config):
#        print("Controller.__init__()")
        self.flavor = config.get('Flavor', '').lower()
        self.host = config.get('Hostname / IP', None)
        self.boot_wait = config.get('Boot Wait', 0)
        self.shutdown_wait = config.get('Shutdown Wait', 0)
        self.tasmota = Tasmota(config.get('Tasmota', None)) if config.get('Tasmota', None) else None
        self.wemo = WeMo(config.get('WeMo', None)) if config.get('WeMo', None) else None

    def power_on(self):
        import time

        if self.tasmota:
            self.tasmota.on()
        elif self.wemo:
            self.wemo.on()
        else:
            raise ValueError('No smart plug found.  Please check your `Controller` configuration')

        print(f"Waiting {self.boot_wait}s for Controller to Boot")
        time.sleep(self.boot_wait)

    def power_off(self):
        import requests, time
        print("Sending Shutdown Signal")
        response = requests.put(f"http://{self.host}/api/shutdown")
#        print(response)
        print(f"Waiting {self.shutdown_wait}s for Controller to Shutdown")
        time.sleep(self.shutdown_wait)

        print("Powering off Controller")
        if self.tasmota:
            self.tasmota.off()
        elif self.wemo:
            self.wemo.off()
        else:
            raise ValueError('No smart plug found.  Please check your `Controller` configuration')

    @property
    def is_on(self):
        if self.tasmota:
            return self.tasmota.is_on
        elif self.wemo:
            return self.wemo.is_on
        else:
            raise ValueError('No smart plug found.  Please check your `Controller` configuration')

    @property
    def is_off(self):
        return not self.is_on

    @property
    def state(self):
        import requests
        return requests.get(f"http://{self.host}/state").text
