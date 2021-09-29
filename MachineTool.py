class StopPoint():
    def __init__(self, machine_tool: 'MachineTool') -> None:
        self.x = machine_tool.x_position
        self.y = machine_tool.y_position + machine_tool.width/2 + 1700


class Conveyor:
    def __init__(self, x, y,  width=5000, length=5000) -> None:
        self.width = width
        self.length = length
        # x, y - середина станка
        self.x_position = x
        self.y_position = y
        self.stop_point = StopPoint(self)
        self.all_machine_tools.append(self)


class MachineTool(Conveyor):
    all_machine_tools = []

    def __init__(self, x, y,  width=3550, length=6510) -> None:
        super().__init__(x, y,  width, length)


class LoaderRobot:
    def __init__(self, speed=12) -> None:
        # скорость в метрах в минуту первожу в миллиметры в секунду
        self.speed = speed*1000 / 60


machine_tool_1 = MachineTool(9455, 2475)
machine_tool_2 = MachineTool(16465, 2475)
machine_tool_3 = MachineTool(23475, 2475)
machine_tool_3 = MachineTool(30485, 2475)
print(machine_tool_1.stop_point.y)
print(LoaderRobot().speed)
