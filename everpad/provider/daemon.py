import sys
sys.path.insert(0, '../..')
from everpad.provider.service import ProviderService
from everpad.provider.sync import SyncThread
from everpad.provider.tools import get_auth_token
from PySide.QtCore import QCoreApplication, Slot
import dbus
import dbus.mainloop.glib
import signal
import fcntl


class ProviderApp(QCoreApplication):
    def __init__(self, *args, **kwargs):
        QCoreApplication.__init__(self, *args, **kwargs)
        session_bus = dbus.SessionBus()
        self.bus = dbus.service.BusName("com.everpad.Provider", session_bus)
        self.service = ProviderService(session_bus, '/EverpadProvider')
        self.sync_thread = SyncThread()
        if get_auth_token():
            self.sync_thread.start()
        self.service.qobject.authenticate_signal.connect(
            self.on_authenticated,
        )
        self.service.qobject.remove_authenticate_signal.connect(
            self.on_remove_authenticated,
        )

    @Slot()
    def on_authenticated(self):
        self.sync_thread.start()

    @Slot()
    def on_remove_authenticated(self):
        self.sync_thread.quit()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    fp = open('/tmp/everpad-provider.lock', 'w')
    fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    app = ProviderApp(sys.argv)
    app.exec_()

if __name__ == '__main__':
    main()