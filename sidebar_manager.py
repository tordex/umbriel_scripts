import asyncio
import os
from enum import Enum

from output import Output
from window import Window
from workspace import Workspace


class Side(Enum):
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"

UPDATE_DELAY = 0.5

struts_sizes = {
    Side.LEFT: 400,
    Side.RIGHT: 400,
    Side.TOP: 100,
    Side.BOTTOM: 100
}

class Struts:
    def __init__(self, workspace_id: str, size: int, side: Side, gap: int = 0):
        self.workspace_id = workspace_id
        self.size = size
        self.side = side
        self.windows = []
        self.gap = gap

    def add_window(self, window: Window):
        self.windows.append(window)
        window.make_floating(True)
        self.update()

    def update(self):
        workspace = Workspace.get_workspace(self.workspace_id)
        if workspace is None:
            return

        output = Output.get_output(workspace.output)
        if output is None:
            return

        self.recalculate_positions(usable_x=output.usable_x, 
                                   usable_y=output.usable_y, 
                                   usable_width=output.usable_width, 
                                   usable_height=output.usable_height)

    def recalculate_positions(self, usable_x: int, usable_y: int, usable_width: int, usable_height: int):
        # Placeholder for recalculating window positions based on the strut size and side.
        # This method should be implemented with the actual logic for repositioning windows.
        pass

    def has_window(self, window: Window) -> bool:
        return any(w.id == window.id for w in self.windows)

    def handle_window_changed(self, window: Window):
        new_windows = []
        ret = False
        for w in self.windows:
            if w.id == window.id:
                if window.floating:
                    if self.update_sizes(window):
                        print(f"[Struts] Updated sizes for window {window.id}")
                        ret = True
                    new_windows.append(window)
                else:
                    print(f"[Struts] Removing window {window.id} from strut")
                    ret = True
            else:
                new_windows.append(w)
        self.windows = new_windows
        return ret

    def handle_window_closed(self, window: Window) -> bool:
        new_windows = []
        ret = False
        for w in self.windows:
            if w.id == window.id:
                print(f"[Struts] Removing window {window.id} from strut due to closure")
                ret = True
            else:
                new_windows.append(w)
        self.windows = new_windows
        return ret

    def update_sizes(self, window: Window) -> bool:
        return False


class StrutsLeft(Struts):
    def __init__(self, workspace: str, size: int):
        super().__init__(workspace_id=workspace, size=size, side=Side.LEFT, gap=0)

    def recalculate_positions(self, usable_x: int, usable_y: int, usable_width: int, usable_height: int):
        if len(self.windows) == 0:
            return
        windows_left = 0
        windows_width = self.size
        windows_height = int(usable_height / len(self.windows) - self.gap * (len(self.windows) - 1))

        width_fract = windows_width / usable_width
        height_fract = windows_height / usable_height

        for i, window in enumerate(self.windows):
            window.set_extent(width_fract, height_fract)
            window.set_position(windows_left, i * (windows_height + self.gap))

    def update_sizes(self, window: Window) -> bool:
        if window.width != self.size:
            print(f"[StrutsLeft] Updating size from {self.size} to {window.width}")
            self.size = window.width
            return True
        return False


class StrutsRight(Struts):
    def __init__(self, workspace: str, size: int):
        super().__init__(workspace_id=workspace, size=size, side=Side.RIGHT, gap=0)

    def recalculate_positions(self, usable_x: int, usable_y: int, usable_width: int, usable_height: int):
        if len(self.windows) == 0:
            return
        windows_left = usable_width - self.size
        windows_width = self.size
        windows_height = int(usable_height / len(self.windows) - self.gap * (len(self.windows) - 1))

        width_fract = windows_width / usable_width
        height_fract = windows_height / usable_height

        for i, window in enumerate(self.windows):
            window.set_extent(width_fract, height_fract)
            window.set_position(windows_left, (i * (windows_height + self.gap)))

    def update_sizes(self, window: Window):
        if window.width != self.size:
            self.size = window.width
            return True
        return False


class StrutsTop(Struts):
    def __init__(self, workspace: str, size: int):
        super().__init__(workspace_id=workspace, size=size, side=Side.TOP, gap=0)

    def recalculate_positions(self, usable_x: int, usable_y: int, usable_width: int, usable_height: int):
        if len(self.windows) == 0:
            return
        windows_top = 0
        windows_height = self.size
        windows_width = int(usable_width / len(self.windows) - self.gap * (len(self.windows) - 1))

        width_fract = windows_width / usable_width
        height_fract = windows_height / usable_height

        for i, window in enumerate(self.windows):
            window.set_extent(width_fract, height_fract)
            window.set_position(i * windows_width, windows_top)

    def update_sizes(self, window: Window):
        if window.height != self.size:
            self.size = window.height
            return True
        return False


class StrutsBottom(Struts):
    def __init__(self, workspace: str, size: int):
        super().__init__(workspace_id=workspace, size=size, side=Side.BOTTOM, gap=0)

    def recalculate_positions(self, usable_x: int, usable_y: int, usable_width: int, usable_height: int):
        if len(self.windows) == 0:
            return
        windows_top = usable_height - self.size
        windows_height = self.size
        windows_width = int(usable_width / len(self.windows) - self.gap * (len(self.windows) - 1))

        width_fract = windows_width / usable_width
        height_fract = windows_height / usable_height

        for i, window in enumerate(self.windows):
            window.set_extent(width_fract, height_fract)
            window.set_position(i * windows_width, windows_top)

    def update_sizes(self, window: Window):
        if window.height != self.size:
            self.size = window.height
            return True
        return False


class SidebarManager:
    def __init__(self):
        self.struts : list[Struts] = []
        self._update_task: asyncio.Task | None = None
        self.umbriel_config_path = f"{os.environ['XDG_RUNTIME_DIR']}/umbriel-sidebar.toml"

    def __del__(self):
        if os.path.exists(self.umbriel_config_path):
            os.remove(self.umbriel_config_path)

    def dock_window(self, side: Side):
        focused_window = Window.get_focused_window()
        if not focused_window:
            return False

        window = focused_window

        strut_found = None
        for strut in self.struts:
            if strut.side == side and strut.workspace_id == window.workspace:
                strut_found = strut
                break
        if strut_found is None:
            if side == Side.LEFT:
                strut_found = StrutsLeft(workspace=window.workspace, size=struts_sizes[Side.LEFT])
            elif side == Side.RIGHT:
                strut_found = StrutsRight(workspace=window.workspace, size=struts_sizes[Side.RIGHT])
            elif side == Side.TOP:
                strut_found = StrutsTop(workspace=window.workspace, size=struts_sizes[Side.TOP])
            elif side == Side.BOTTOM:
                strut_found = StrutsBottom(workspace=window.workspace, size=struts_sizes[Side.BOTTOM])
            self.struts.append(strut_found)
        
        strut_found.add_window(window)
        self.update_umbriel_config()


    def update_umbriel_config(self):
        workspaces = {}
        for strut in self.struts:
            if strut.workspace_id not in workspaces:
                ws = Workspace.get_workspace(strut.workspace_id)
                workspaces[strut.workspace_id] = {
                    "index": ws.index if ws else -1,
                    "output": ws.output if ws else "",
                    "struts": [],
                }
            workspaces[strut.workspace_id]["struts"].append({
                "side": strut.side.value,
                "size": strut.size,
            })

        config = ""
        for ws_data in workspaces.values():
            config += "[[workspace]]\n"
            config += f"index = {ws_data['index']}\n"
            config += f"output = \"{ws_data['output']}\"\n"
            for strut in ws_data["struts"]:
                config += f"layout.struts.{strut['side']} = {strut['size']}\n"
            config += "\n"
            
        with open(self.umbriel_config_path, "w") as f:
            f.write(config)

    def update(self):
        # Debounced: each call restarts the timer.
        if self._update_task is not None:
            self._update_task.cancel()
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            self._do_update()
            return
        self._update_task = loop.create_task(self._delayed_update())

    async def _delayed_update(self):
        await asyncio.sleep(UPDATE_DELAY)
        self._update_task = None
        self._do_update()

    def _do_update(self):
        for strut in self.struts:
            strut.update()
        self.update_umbriel_config()

    def handle_window_changed(self, window_data: dict):
        updates = False
        new_struts = []
        window = Window.from_data(window_data)
        for strut in self.struts:
            if strut.handle_window_changed(window):
                updates = True
                print(f"[SidebarManager] Strut for workspace {strut.workspace_id} has been updated.")
            if len(strut.windows) != 0:
                new_struts.append(strut)
            else:
                updates = True
                print(f"[SidebarManager] Removing empty strut for workspace {strut.workspace_id}")
        self.struts = new_struts
        if updates:
            print("[SidebarManager] Updates detected, updating struts and Umbriel config.")
            self.update()

    def handle_window_closed(self, window_data: dict):
        window = Window.from_data(window_data)
        updates = False
        new_struts = []
        for strut in self.struts:
            if strut.handle_window_closed(window):
                updates = True
                print(f"[SidebarManager] Strut for workspace {strut.workspace_id} has been updated due to window closure.")
            if len(strut.windows) != 0:
                new_struts.append(strut)
            else:
                updates = True
                print(f"[SidebarManager] Removing empty strut for workspace {strut.workspace_id}")
        self.struts = new_struts
        if updates:
            print("[SidebarManager] Updates detected, updating struts and Umbriel config.")
            self.update()
