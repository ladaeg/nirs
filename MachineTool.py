conv_width = 5000
conv_length = 5000
mt_width = 3550
mt_length = 6510
distance_to_wall = 1000
distance_bw_mt = 700
robot_hand_length = 1500


class StopPoint():
    def __init__(self, some_tool) -> None:
        self.x = some_tool.x_position
        self.y = some_tool.y_position + some_tool.width/2 + robot_hand_length


class ToolDescription():
    all_tools = []

    def __init__(self, x, y, width, length, orientation=0) -> None:
        self.width = width
        self.length = length
        # x, y - середина оборудования
        self.x_position = x
        self.y_position = y
        self.orientation = orientation
        self.stop_point = StopPoint(self)
        self.all_tools.append(self)


class Conveyor(ToolDescription):
    def __init__(self, x, y,  width=conv_width, length=conv_length, orientation=0) -> None:
        super().__init__(x, y,  width, length, orientation)


class MachineTool(ToolDescription):
    def __init__(self, x, y,  width=mt_width, length=mt_length, orientation=270) -> None:
        super().__init__(x, y,  width, length, orientation)


class LoaderRobot:
    def __init__(self, speed=12) -> None:
        # скорость в метрах в минуту первожу в миллиметры в секунду
        self.speed = speed*1000 / 60


conveyor_1 = Conveyor(distance_to_wall + conv_length/2,
                      distance_to_wall + mt_width + robot_hand_length)
machine_tool_1 = MachineTool(conveyor_1.x_position + conv_length/2 + robot_hand_length + mt_length/2,
                             distance_to_wall + mt_width/2)
machine_tool_2 = MachineTool(machine_tool_1.x_position + mt_length + distance_bw_mt,
                             distance_to_wall + mt_width/2)
machine_tool_3 = MachineTool(machine_tool_2.x_position + mt_length + distance_bw_mt,
                             distance_to_wall + mt_width/2)
machine_tool_4 = MachineTool(machine_tool_3.x_position + mt_length + distance_bw_mt,
                             distance_to_wall + mt_width/2)
print(machine_tool_1.stop_point.y)
print(LoaderRobot().speed)
