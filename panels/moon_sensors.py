import logging
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango
from ks_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):
    def __init__(self, screen, title):
        title = title or _("Sensors")
        super().__init__(screen, title)
        self.devices = {}
        # Create a grid for all devices
        self.labels['devices'] = Gtk.Grid(valign=Gtk.Align.CENTER)

        #self.load_sensors()

        # Create a scroll window for the power devices
        scroll = self._gtk.ScrolledWindow()
        scroll.add(self.labels['devices'])

        self.content.add(scroll)

    def activate(self):
        self.load_sensors()

    def add_sensor(self, device):
        name = Gtk.Label(
            hexpand=True, vexpand=True, halign=Gtk.Align.START, valign=Gtk.Align.CENTER,
            wrap=True, wrap_mode=Pango.WrapMode.WORD_CHAR)
        name.set_markup(f"<big><b>{device}</b></big>")

        labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        labels.add(name)
        
        params_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sensors = self._printer.get_moon_sensor_params(device)
        params = {}
        for param, value in sensors.items():
            param_value_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

            param_label = Gtk.Label(hexpand=True, halign=Gtk.Align.START)
            param_label.set_markup(f"{param}")
            param_value_box.add(param_label)

            value_label = Gtk.Label(halign=Gtk.Align.END)
            value_label.set_label(f"{value}")
            param_value_box.add(value_label)
            params[param] = value_label
            params_box.add(param_value_box)

        dev = Gtk.Box(
            spacing=5, hexpand=True, vexpand=False, valign=Gtk.Align.CENTER, orientation=Gtk.Orientation.VERTICAL)
        dev.add(labels)
        dev.add(params_box)

        self.devices[device] = {
            "row": dev,
            "params": params
        }

        devices = sorted(self.devices)
        pos = devices.index(device)

        self.labels['devices'].insert_row(pos)
        self.labels['devices'].attach(self.devices[device]['row'], 0, pos, 1, 1)

    def load_sensors(self):
        for child in self.labels['devices'].get_children():
            self.labels['devices'].remove(child)
        
        sensors = self._printer.get_moon_sensors()
        for x in sensors:
            self.add_sensor(x)

        self.labels['devices'].show_all()

    def process_update(self, action, data):
        if action == "notify_sensor_update":
            devices = self._printer.get_moon_sensors()
            for device in devices:
                if device in self.devices:
                    sensors = self._printer.get_moon_sensor_params(device)
                    if sensors is not None:
                        for param, value in sensors.items():
                            if param in self.devices[device]["params"]:
                                self.devices[device]["params"][param].set_label(f"{value}")
