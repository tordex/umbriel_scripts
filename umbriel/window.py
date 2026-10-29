import umbriel.ipc


# Define the window class to encapsulate its properties and actions.
class Window:
    """Class representing a window."""

    def __init__(self, data: dict | None = None):
        if data is None:
            self.id : str = ""
            self.active  : bool = False
            self.floating : bool = False
            self.width : int = 0
            self.height : int = 0
            self.x : int = 0
            self.y : int = 0
            self.workspace : str = ""
            self.output : str = ""
        else:
            self.id : str = data["id"]
            self.active  : bool = data["active"]
            self.floating : bool = data["floating"]
            self.width : int = data["w"]
            self.height : int = data["h"]
            self.x : int = data["x"]
            self.y : int = data["y"]
            self.workspace : str = data["workspace"]
            self.output : str = data["output"]

    def update_from_window(self, window: "Window"):
        self.id = window.id
        self.active = window.active
        self.floating = window.floating
        self.width = window.width
        self.height = window.height
        self.x = window.x
        self.y = window.y
        self.workspace = window.workspace
        self.output = window.output

    def make_floating(self, floating: bool = True):
        if self.floating != floating:
            self.floating = floating
            umbriel.ipc.window_toggle_floating(self.id)

    def focus(self):
        return umbriel.ipc.window_focus(self.id)

    def set_position(self, x: int, y: int):
        return umbriel.ipc.window_move_to(umbriel.ipc.Anchor.TOP_LEFT, x, y, self.id)

    def set_extent(self, width: float, height: float):
        focused_window = self.get_focused_window()
        if focused_window is None:
            return False
        self.focus()
        result_primary = umbriel.ipc.window_set_primary_extent(width)
        result_secondary = umbriel.ipc.window_set_secondary_extent(height)
        result_focus = focused_window.focus()
        return result_primary and result_secondary and result_focus

    @staticmethod
    def get_window(window_id):
        """Get window information using niri."""
        window_data = umbriel.ipc.send_query("windows", jq_query=f'.[] | select(.id == "{window_id}")')
        if window_data:
            return Window(window_data)
        return None

    @staticmethod
    def get_focused_window():
        """Get the currently focused window using niri."""
        window_data = umbriel.ipc.send_query("focused-window")
        if window_data:
            window_obj = Window(window_data)
            return window_obj
        return None

    @staticmethod
    def from_data(data):
        """Create a Window instance from raw data."""
        return Window(data)
