import umbriel.ipc


class Output:
    """Class representing an output (monitor/display)."""

    def __init__(self, data: dict | None = None):
        if data is None:
            self.name : str = ""
            self.focused : bool = False
            self.enabled : bool = False
            self.powered : bool = False
            self.scale : float = 1.0
            self.transform : str = ""
            self.usable_x : int = 0
            self.usable_y : int = 0
            self.usable_width : int = 0
            self.usable_height : int = 0
        else:
            self.name : str = data["name"]
            self.focused : bool = data["focused"]
            self.enabled : bool = data["enabled"]
            self.powered : bool = data["powered"]
            self.scale : float = data["scale"]
            self.transform : str = data["transform"]
            self.active_workspace : str = data["active_workspace"]
            self.usable_x : int = data["usable_area"]["x"]
            self.usable_y : int = data["usable_area"]["y"]
            self.usable_width : int = data["usable_area"]["width"]
            self.usable_height : int = data["usable_area"]["height"]

    @staticmethod
    def get_output(name):
        """Get output information using niri."""
        output_data = umbriel.ipc.send_query("outputs", jq_query=f'.[] | select(.name == "{name}")')
        if output_data:
            return Output(output_data)
        return None

    @staticmethod
    def get_focused_outputs():
        """Get all active outputs using niri."""
        outputs_data = umbriel.ipc.send_query("outputs", jq_query='.[] | select(.focused)')
        if outputs_data:
            return Output(outputs_data)
        return None
