from umbriel import utils


# Define the monitor and window classes to encapsulate their properties and actions.
class monitor:
    """Class representing a monitor."""

    def __init__(self):
        self.data = None

    def get_name(self):
        """Get the name of the monitor."""
        return self.data.get("name") if self.data else ""

    def get_logical_width(self):
        """Get the logical width of the monitor."""
        return self.data.get("logical", {}).get("width") if self.data else 0

    def get_logical_height(self):
        """Get the logical height of the monitor."""
        return self.data.get("logical", {}).get("height") if self.data else 0

    def make_focused(self):
        """Make this monitor the focused monitor."""
        if self.data:
            command = ["niri", "msg", "action", "focus-monitor", self.get_name()]
            return utils.run_command(command)
        return False

    @staticmethod
    def from_id(name):
        """Create a monitor object from a monitor ID."""
        command = ["niri", "msg", "--json", "outputs"]
        data = utils.run_command_json(command)
        if data is not None:
            for monitor_name, monitor_data in data.items():
                if monitor_name == name:
                    monitor_obj = monitor()
                    monitor_obj.data = monitor_data
                    return monitor_obj
        return None

    @staticmethod
    def get_active_monitor():
        """Get the active monitor using niri."""
        command = ["niri", "msg", "--json", "focused-output"]
        monitor_data = utils.run_command_json(command)
        if monitor_data:
            monitor_obj = monitor()
            monitor_obj.data = monitor_data
            return monitor_obj
        return None
