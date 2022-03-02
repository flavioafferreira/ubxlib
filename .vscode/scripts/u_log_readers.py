import time
from serial import Serial
from pylink import JLink
from pylink.enums import JLinkInterfaces

class URttReader:
    """A simple JLink RTT reader"""
    def __init__(self, device, jlink_serial=None,
                 jlink_logfile=None, reset_on_connect=False):
        """device: The JLink device to connect"""
        self.device = device
        self.serial = jlink_serial
        self.jlink = JLink()
        self.jlink_logfile = jlink_logfile
        self.reset_on_connect = reset_on_connect

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type_, value, traceback):
        self.close()

    def connect(self):
        self.jlink.open(serial_no=self.serial)
        if self.jlink_logfile:
            self.jlink.set_log_file(self.jlink_logfile)
        print(f"Connecting to {self.device}")
        self.jlink.set_tif(JLinkInterfaces.SWD)
        self.jlink.connect(self.device)
        if self.reset_on_connect:
            print(f"Resetting target")
            self.jlink.reset(halt=False)
        print("Enabling RTT")
        self.jlink.rtt_start(None)

    def close(self):
        """Closes the JLink connection"""
        print("Disabling RTT")
        self.jlink.rtt_stop()
        print("Closing connection")
        self.jlink.close()

    def read(self, timeout=0.5):
        """Reads the JLink RTT buffer
        If there are no new data available until timeout hits
        this function will return None"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            data = self.jlink.rtt_read(0, 4096)
            if (len(data) > 0):
                # We got the data
                return data
            else:
                # No data - try again later
                time.sleep(0.1)
        return None


class UUartReader(Serial):
    """A PySerial wrapper that will set RTS and DTR state on open
    dtr_state: Set to True to turn on DTR on open, false to to turn off
               DTR on open. If not specified (or set to None) DTR will be
               left untouched on open.
    rts_state: Set to True to turn on RTS on open, false to to turn off
               RTS on open. If not specified (or set to None) RTS will be
               left untouched on open.
    """
    def __init__(self, dtr_state=None, rts_state=None, *args, **kwargs):
        self.dtr_state=dtr_state
        self.rts_state=rts_state
        super(UUartReader, self).__init__(*args, **kwargs)

    def open(self, *args, **kwargs):
        print(f"Opening {self.port}")
        super(UUartReader, self).open(*args, **kwargs)
        if self.dtr_state is not None:
            print("Setting DTR {}".format("on" if self.dtr_state else "off"))
            self.dtr = self.dtr_state
        if self.rts_state is not None:
            print("Setting RTS {}".format("on" if self.rts_state else "off"))
            self.rts = self.rts_state


