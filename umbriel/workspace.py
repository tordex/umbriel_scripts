import umbriel.ipc


class Workspace:
    """Class representing a workspace."""

    def __init__(self, data: dict | None = None):
        if data is None:
            self.id : str = ""
            self.focused : bool = False
            self.active : bool = False
            self.index : int = 0
            self.layout : str = ""
            self.named : bool = False
            self.name : str = ""
            self.output : str = ""
            self.focused_window : str = ""
        else:
            self.id : str = data["id"]
            self.focused : bool = data["focused"]
            self.active : bool = data["active"]
            self.index : int = data["index"]
            self.layout : str = data["layout"]
            self.named : bool = data["named"]
            self.name : str = data["name"]
            self.output : str = data["output"]
            self.focused_window : str = data["focused_window"]

    @staticmethod
    def get_workspace(id):
        """Get workspace information"""
        workspace_data = umbriel.ipc.send_query("workspaces", jq_query=f'.[] | select(.id == "{id}")')
        if workspace_data:
            return Workspace(workspace_data)
        return None

    @staticmethod
    def get_focused():
        """Get the currently focused workspace"""
        workspace_data = umbriel.ipc.send_query("workspaces", jq_query='.[] | select(.focused) | select(.active)')
        if workspace_data:
            return Workspace(workspace_data)
        return None
