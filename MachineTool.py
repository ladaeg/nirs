from math import pi, sin, cos


conv_width = 5000
conv_length = 5000
mt_width = 3550
mt_length = 6510
distance_to_wall = 1000
distance_bw_mt = 700
robot_hand_length = 1500

work_time_hours = 8
work_time_sec = work_time_hours*60*60
work_time_fact = 0


def arifm_round(num) -> float:
    num = int(num + (0.5 if num > 0 else -0.5))
    return num


class StopPoint():
    def __init__(self, tool: 'BaseTool') -> None:
        cur_cos = arifm_round(cos(tool.orientation))
        cur_sin = arifm_round(sin(tool.orientation))
        if (cur_cos+cur_sin) == 1 or (cur_cos+cur_sin) == -1:
            self.x = tool.x_сentre + cur_cos * \
                (tool.length/2 + robot_hand_length)
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
    mt_order = []

    def __init__(self, x, y, width=mt_width, length=mt_length, orientation=(-pi/2)) -> None:
        super().__init__(x, y,  width, length, orientation)
        self.mt_list.append(self)
        self.details_list = []
        self.unload_flag = False
        self.process_time_left = 0
        self.cur_detail_num = 0

    def add_detail(self, process_time, amount):
        detail = Detail(process_time, amount)
        self.details_list.append(detail)

    def start_process(self):
        try:
            cur_detail = self.details_list[self.cur_detail_num]
            cur_detail.fact_amount += 1
            self.process_time_left = cur_detail.process_time
            MachineTool.update_order()
            if cur_detail.fact_amount == cur_detail.amount:
                self.cur_detail_num += 1
                self.details_list[self.cur_detail_num]

        except IndexError:
            print(f'Нет деталей в списке! - {self} {self.unload_flag}')
            if self.unload_flag:
                self.mt_order.remove(self)
            else:
                self.unload_flag = True

    @classmethod
    def update_order(cls, time=0):
        for tool in cls.mt_order:
            if time <= tool.process_time_left:
                tool.process_time_left -= time
            else:
                tool.process_time_left = 0

            global work_time_sec, work_time_fact
            if work_time_sec-work_time_fact < tool.process_time_left:
                cls.mt_order.remove(tool)

        cls.mt_order.sort(key=lambda tool: tool.process_time_left)


class Detail:
    def __init__(self, process_time, amount) -> None:
        self.process_time = process_time
        self.amount = amount
        self.fact_amount = 0


class Robot:

    def __init__(self, speed=12, load_time=5) -> None:
        # скорость в метрах в минуту первожу в миллиметры в секунду
        self.speed = speed*1000 / 60
        self.load_time = load_time
        self.work_time = work_time_sec
        self.conv = Conveyor.conv_list[0]
        self.cur_tool = self.conv
        self.set_all_pathes()

    def unload(self, cur_tool):
        self.go_to(cur_tool)
        global work_time_fact
        self.work_time -= cur_tool.process_time_left
        work_time_fact += cur_tool.process_time_left
        self.add_load_time()
        self.go_to(self.conv)
        self.add_load_time()

    def download(self, cur_tool: 'MachineTool'):
        if not cur_tool.unload_flag:
            self.go_to(self.conv)   # идет к конвееру
            self.add_load_time()    # кладет деталь
            self.add_load_time()    # берет заготовку
            self.go_to(cur_tool)    # идет к станку

            # ждет пока текущий станок закончит обработку
            global work_time_fact
            self.work_time -= cur_tool.process_time_left
            work_time_fact += cur_tool.process_time_left
            MachineTool.update_order(cur_tool.process_time_left)

            self.add_load_time()    # снимает деталь
            self.add_load_time()    # устанавливает заготовку
        else:
            self.unload(cur_tool)

    def add_load_time(self):
        global work_time_fact

        work_time_fact += self.load_time
        MachineTool.update_order(self.load_time)

    def go_to(self, tool):
        global work_time_fact

        path_time = self.all_pathes_time.get(self.cur_tool)
        work_time_fact += path_time
        MachineTool.update_order(path_time)
        self.cur_tool = tool

    def set_all_pathes(self):
        if len(Conveyor.conv_list) == 1:
            for tool in MachineTool.mt_list:
                if self.conv.stop_point.x != tool.stop_point.x:
                    break
            else:
                self.calculate_path_time()

            for tool in MachineTool.mt_list:
                if self.conv.stop_point.y != tool.stop_point.y:
                    print('Станки должны находиться на одной горизонтальной или вертикальной линии с конвеером!')
                    break
            else:
                self.calculate_path_time()
        else:
            print('Ожидается один конвеер!')

    def calculate_path_time(self) -> None:
        self.all_pathes_time = {}
        self.all_pathes_time.update({self.conv: 0})

        for tool in MachineTool.mt_list:
            path = abs(self.conv.stop_point.x-tool.stop_point.x) + \
                (self.conv.stop_point.y-tool.stop_point.y)
            time_path = arifm_round(path/self.speed)
            self.all_pathes_time.update({tool: time_path})


if __name__ == '__main__':
    conveyor_1 = Conveyor(distance_to_wall + conv_length/2,
                          distance_to_wall + mt_width + robot_hand_length)

    machine_tool_1 = MachineTool(conveyor_1.x_сentre + conv_length/2 + robot_hand_length + mt_length/2,
                                 distance_to_wall + mt_width/2)
    machine_tool_1.add_detail(500, 50)
    machine_tool_1.add_detail(200, 15)

    machine_tool_2 = MachineTool(machine_tool_1.x_сentre + mt_length + distance_bw_mt,
                                 distance_to_wall + mt_width/2)
    machine_tool_2.add_detail(600, 50)
    machine_tool_2.add_detail(200, 25)

    machine_tool_3 = MachineTool(machine_tool_2.x_сentre + mt_length + distance_bw_mt,
                                 distance_to_wall + mt_width/2)
    machine_tool_3.add_detail(1100, 50)

    machine_tool_4 = MachineTool(machine_tool_3.x_сentre + mt_length + distance_bw_mt,
                                 distance_to_wall + mt_width/2)
    machine_tool_4.add_detail(200, 10)

    robot = Robot()

    MachineTool.mt_order = MachineTool.mt_list[:]

    while work_time_fact < work_time_sec:
        try:
            cur_tool = MachineTool.mt_order[0]
            robot.download(cur_tool)
            cur_tool.start_process()
        except IndexError:
            break

    print(f'Очередь на загрузку пуста - рабочий день окончен! - {work_time_fact} {robot.work_time} {work_time_sec}')
    for tool in MachineTool.mt_list:
        for detail in tool.details_list:
            print(f'{tool} - {detail.fact_amount}')
