MACHINE = '\033[91m'
ENDC = '\033[0m'

class Machine:

    MILL = 'Mill'
    LATHE = 'Lathe'

    def __init__(self, name=None, type=MILL, feed=500):
        if not type in [self.MILL, self.LATHE]:
            raise ValueError(f"Machine type ({type}) must be Machine.MILL or Machine.LATHE")
        self._type = type
        self._feed = feed
        if name is None:
            self._name = type
        else:
            self._name = name
        print(f";{MACHINE} Initializing a {self.type} named {self.name}{ENDC}")

    def new_tool(self):
        from .tool import Tool
        return Tool(self)

    @property
    def type(self):
        return self._type

    @type.setter
    def name (self, value):
        print(f";{MACHINE} Setting {self.name} machine type: {value}{ENDC}")
        self._type = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name (self, value):
        print(f";{MACHINE} Renaming {self.name}: {value}{ENDC}")
        self._name = value

    @property
    def safe_z(self):
        return self._safe_z

    @safe_z.setter
    def safe_z (self, value):
        print(f";{MACHINE} Setting {self.name} Safe Z: {value}{ENDC}")
        self._safe_z = value

    @property
    def max_rpm(self):
        return self._max_rpm

    @max_rpm.setter
    def max_rpm(self, value):
        print(f";{MACHINE} Setting {self.name} max Spindle RPM: {value}{ENDC}")
        self._max_rpm = value

    @property
    def max_feed(self):
        return self._max_feed

    @max_feed.setter
    def max_feed(self, value):
        print(f";{MACHINE} Setting {self.name} max Feed: {value}mm/min{ENDC}")
        self._max_feed = value
