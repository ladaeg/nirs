from math import pi, sin, cos


conv_width = 5000
conv_length = 5000
mt_width = 3550
mt_length = 6510
distance_to_wall = 1000
distance_bw_mt = 700
robot_hand_length = 1500


def arifm_round(num):
    num = int(num + (0.5 if num > 0 else -0.5))
    return num


class StopPoint():
    def __init__(self, tool: 'BaseTool') -> None:
        cur_cos = arifm_round(cos(tool.orientation))
        cur_sin = arifm_round(sin(tool.orientation))
        if (cur_cos+cur_sin) == 1 or (cur_cos+cur_sin) == -1:
            self.x = tool.x_сentre + cur_cos*(tool.length/2 + robot_hand_length)
            self.y = tool.y_centre - cur_sin*(tool.width/2 + robot_hand_length)
        else:
            print('Ошибка в задании положения станка!')


class BaseTool():
    def __init__(self, x, y, width, length, orientation=0) -> None:
        # x, y - середина оборудования
        self.x_сentre = x
        self.y_centre = y
        self.width = width
        self.length = length
        self.orientation = orientation
        self.stop_point = StopPoint(self)


class Conveyor(BaseTool):
    conv_list = []

    def __init__(self, x, y,  width=conv_width, length=conv_length, orientation=0) -> None:
        super().__init__(x, y,  width, length, orientation)
        self.conv_list.append(self)


class MachineTool(BaseTool):
    mt_list = []

    def __init__(self, x, y,  width=mt_width, length=mt_length, orientation=3*pi/2) -> None:
        super().__init__(x, y,  width, length, orientation)
        self.mt_list.append(self)


class LoaderRobot:
    def __init__(self, speed=12) -> None:
        # скорость в метрах в минуту первожу в миллиметры в секунду
        self.speed = speed*1000 / 60


class RobotPath:
    all_pathes = {}

    def __init__(self) -> None:
        if len(Conveyor.conv_list) == 1:
            self.conveyor = Conveyor.conv_list[0]
            for tool in MachineTool.mt_list:
                if self.conveyor.stop_point.x != tool.stop_point.x:
                    break
            else:
                self.calculate_distance(Conveyor.conv_list, MachineTool.mt_list)

            for tool in MachineTool.mt_list:
                if self.conveyor.stop_point.y != tool.stop_point.y:
                    print('Станки должны находиться на одной горизонтальной или вертикальной линии с конвеером!')
                    break
            else:
                self.calculate_distance(Conveyor.conv_list, MachineTool.mt_list)
        else:
            print('Ожидается один конвеер!')

    def calculate_distance(self, conveyors, machine_tools):
        for tool in MachineTool.mt_list:
            path = (self.conveyor.stop_point.x-tool.stop_point.x) + (self.conveyor.stop_point.y-tool.stop_point.y)
            self.all_pathes.update({tool: abs(path)})


conveyor_1 = Conveyor(distance_to_wall + conv_length/2, distance_to_wall + mt_width + robot_hand_length)
machine_tool_1 = MachineTool(conveyor_1.x_сentre + conv_length/2 + robot_hand_length + mt_length/2,
                             distance_to_wall + mt_width/2)
machine_tool_2 = MachineTool(machine_tool_1.x_сentre + mt_length + distance_bw_mt, distance_to_wall + mt_width/2)
machine_tool_3 = MachineTool(machine_tool_2.x_сentre + mt_length + distance_bw_mt, distance_to_wall + mt_width/2)
machine_tool_4 = MachineTool(machine_tool_3.x_сentre + mt_length + distance_bw_mt, distance_to_wall + mt_width/2)
print(machine_tool_1.stop_point.y)
print(LoaderRobot().speed)
print(RobotPath().all_pathes.items())
