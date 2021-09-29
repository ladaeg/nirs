class StopPoint():
    def __init__(self, machine_tool: 'MachineTool') -> None:
        self.x = machine_tool.x_position
        self.y = machine_tool.y_position + machine_tool.width/2 + 100

class MachineTool:
    def __init__(self, x, y,  width = 580, length = 1100) -> None:
        self.width = width
        self.length = length
        # x, y - середина станка
        self.x_position = x
        self.y_position = y
        self.stop_point = StopPoint(self)
        
machine_tool_1 = MachineTool(1250, 980)
print(machine_tool_1.stop_point.y)
