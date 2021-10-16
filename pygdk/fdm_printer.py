from .machine import Machine

class FDMPrinter(Machine):
    def __init__(self, name=None, type=None, max_feed=None, safe_z=10):
        super().__init__(name, type, max_feed, safe_z)
