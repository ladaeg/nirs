from math import pi, sin, cos

# геометрические параметры, определяющие расположение элементов цехе
conv_width = 5000
conv_length = 5000
mt_width = 3550
mt_length = 6510
distance_to_wall = 1000
distance_bw_mt = 700
robot_hand_length = 1500

# рабочее время в цехе
work_time_hours = 8
work_time_sec = work_time_hours*60*60
work_time_fact = 0


def arifm_round(num) -> float:
    """Округляет число до целого по правилам арифметики"""
    num = int(num + (0.5 if num > 0 else -0.5))
    return num


class StopPoint():
    """Точка остановки робота возле станка"""
    def __init__(self, tool: 'BaseTool') -> None:
        cur_cos = arifm_round(cos(tool.orientation))
        cur_sin = arifm_round(sin(tool.orientation))
        # точка установа определяетяс в зависимости от ориентации станка
        if (cur_cos+cur_sin) == 1 or (cur_cos+cur_sin) == -1:
            self.x = tool.x_сentre + cur_cos*(tool.length/2 + robot_hand_length)
            self.y = tool.y_centre - cur_sin*(tool.width/2 + robot_hand_length)
        else:
            print('Ошибка в задании положения станка!')


class BaseTool():
    """Базовое описание оборудования"""
    def __init__(self, x, y, width, length, orientation=0) -> None:
        # x, y - середина оборудования
        self.x_сentre = x
        self.y_centre = y
        self.width = width
        self.length = length
        self.orientation = orientation
        self.stop_point = StopPoint(self)


class Conveyor(BaseTool):
    """Описание конвеера"""
    conv_list = []  # список нужен для защиты от создания нескольких конвееров в системе

    def __init__(self, x, y,  width=conv_width, length=conv_length, orientation=0) -> None:
        super().__init__(x, y,  width, length, orientation)
        self.conv_list.append(self)


class MachineTool(BaseTool):
    """Описание станка"""
    mt_list = []    # список всех станков в системе
    mt_order = []   # очередь на обслуживание, которой пользуется робот

    def __init__(self, x, y, width=mt_width, length=mt_length, orientation=(-pi/2), name='defoult') -> None:
        super().__init__(x, y,  width, length, orientation)
        self.mt_list.append(self)

        self.name = name
        if self.name == 'defoult':
            self.name = f'Станок {len(self.mt_list)}'

        self.details_list = []
        self.unload_flag = False    # нужен, чтобы понять когда станок нужно разгрузить
        self.process_time_left = 0  # время до конца обработки текущей детали
        self.cur_detail_num = 0     # отслеживание очереди детали на обработку

    def add_detail(self, process_time, amount, name='defoult'):
        """Добавляет деталь в очередь на обработку на текущем станке"""
        if name == 'defoult':
            name = f'Деталь с{len(self.mt_list)}-д{len(self.details_list)+1}'
        detail = Detail(process_time, amount, name)
        self.details_list.append(detail)

    def start_process(self):
        """Начало обработки"""
        try:
            cur_detail = self.details_list[self.cur_detail_num]     # взять в обработку очередную деталь

            global work_time_sec, work_time_fact
            if cur_detail.process_time < work_time_sec-work_time_fact:
                cur_detail.fact_amount += 1     # установить, что обработана еще одна деталь текущего вида
                self.process_time_left = cur_detail.process_time
            else:   # если время обработки детали на станке больше остатка рабочего времени, ставим сатнок на разгрузку
                self.unload_flag = True
            # обновить очередь станков на обслуживание -> текущий станок сдвинется на другое место
            MachineTool.update_order()
            # если все детали текущего вида обработаны, переходим к следующей в списке
            if cur_detail.fact_amount == cur_detail.amount:
                self.cur_detail_num += 1
                self.details_list[self.cur_detail_num]  # смотрим есть ли в списке еще детали, если нет то except

        except IndexError:
            print(f'Нет деталей в списке! - {self.name}, разгрузка произведена: {self.unload_flag}')
            if self.unload_flag:    # если робот разгрузил станок, то удаляем его из очереди
                self.mt_order.remove(self)
            else:   # если нет, то станок остается в очереди, но с флагом на разгрузку True
                self.unload_flag = True

    @classmethod
    def update_order(cls, time=0):
        """Обновляет очередь станоков"""
        # обновляет время оставшееся до конца обработки на каждом станке
        for tool in cls.mt_order:
            if time <= tool.process_time_left:
                tool.process_time_left -= time
            else:
                tool.process_time_left = 0
        # сортируем список по времени до конца обработки - от меньшего к большему
        cls.mt_order.sort(key=lambda tool: tool.process_time_left)


class Detail:
    """Описание детали"""
    def __init__(self, process_time, amount, name) -> None:
        self.process_time = process_time
        self.amount = amount
        self.name = name
        self.fact_amount = 0    # фактическое колличество призведеных деталей


class Robot:
    """Описание робота-загрузчика"""
    def __init__(self, speed=12, load_time=5, name='Робот') -> None:
        self.speed = speed*1000 / 60    # скорость в метрах в минуту первожу в миллиметры в секунду
        self.load_time = load_time      # скорость загрузки/выгрузки
        self.name = name
        self.work_time = work_time_sec  # изначально допускаю, что робот никогда не останавливает свою работу
        self.conv = Conveyor.conv_list[0]
        self.prev_tool = self.conv       # Текущее оборудование, у которого изначально находится робот
        self.set_all_pathes()

    def unload(self, cur_tool):
        """Разгрузить станок"""
        self.go_to(cur_tool)    # идет к станку
        self.wait()             # ждет пока текущий станок закончит обработку
        self.add_load_time()    # снимает деталь
        self.go_to(self.conv)   # идет к конвееру
        self.add_load_time()    # кладет деталь

    def download(self, cur_tool: 'MachineTool'):
        """Загрузить станок"""
        self.cur_tool = cur_tool
        if not cur_tool.unload_flag:
            self.go_to(self.conv)   # идет к конвееру
            self.add_load_time()    # кладет деталь
            self.add_load_time()    # берет заготовку
            self.go_to(cur_tool)    # идет к станку
            self.wait()             # ждет пока текущий станок закончит обработку
            self.add_load_time()    # снимает деталь
            self.add_load_time()    # устанавливает заготовку
        else:
            self.unload(cur_tool)

    def wait(self):
        """Ждет пока закончится обработка детали"""
        global work_time_fact
        self.work_time -= self.cur_tool.process_time_left    # вычитаю простой робота из его времени работы
        work_time_fact += self.cur_tool.process_time_left
        MachineTool.update_order(self.cur_tool.process_time_left)

    def add_load_time(self):
        """Добавить время закгрузки/выгрузки детали"""
        global work_time_fact
        work_time_fact += self.load_time
        MachineTool.update_order(self.load_time)

    def go_to(self, tool):
        """Идти к оборудованию"""
        # если оборудование - конвеер, то время перемещения равно времени от конвеера до уже обслуженного оборудования
        if type(tool) == Conveyor:
            path_time = self.all_pathes_time.get(self.prev_tool)
        # если - станок, то время перемещения равно времени от конвеера до текущего обслужеваемого оборудования
        elif type(tool) == MachineTool:
            path_time = self.all_pathes_time.get(self.cur_tool)

        global work_time_fact
        work_time_fact += path_time
        MachineTool.update_order(path_time)
        self.prev_tool = tool

    def set_all_pathes(self):
        """Установить время всех премещений"""
        if len(Conveyor.conv_list) == 1:    # защита от нескольких конвееров

            # проверки на нахождение станков и конвеера на одной линии
            for tool in MachineTool.mt_list:
                if self.conv.stop_point.x != tool.stop_point.x:
                    break
            else:
                self.calculate_path_time()  # если все в порядке, находим время перемещений

            for tool in MachineTool.mt_list:
                if self.conv.stop_point.y != tool.stop_point.y:
                    print('Станки должны находиться на одной горизонтальной или вертикальной линии с конвеером!')
                    break
            else:
                self.calculate_path_time()  # если все в порядке, находим время перемещений
        else:
            print('Ожидается один конвеер!')

    def calculate_path_time(self) -> None:
        """Подсчет времени пути от конвеера до всех станков"""
        self.all_pathes_time = {}
        self.all_pathes_time.update({self.conv: 0})

        for tool in MachineTool.mt_list:
            path = abs((self.conv.stop_point.x-tool.stop_point.x) + (self.conv.stop_point.y-tool.stop_point.y))
            time_path = arifm_round(path/self.speed)
            self.all_pathes_time.update({tool: time_path})


class Statistics():
    """Статистика по работе оборудования"""
    def __init__(self, tool: 'Robot' or 'MachineTool') -> None:
        self.tool = tool
        self.tool_work_time = 0
        if type(tool) == Robot:
            self.tool_work_time = tool.work_time
        elif type(tool) == MachineTool:
            for detail in tool.details_list:
                self.tool_work_time += detail.fact_amount*detail.process_time
        self.all_work_time = work_time_sec
        self.load_coef = self.tool_work_time/self.all_work_time

    def __str__(self):
        return f'{self.tool.name} коэффициент загрузки - {self.load_coef}'


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
            print(f'{tool.name} произведено: {detail.fact_amount} - {detail.name}')

    print(Statistics(robot))
    for tool in MachineTool.mt_list:
        print(Statistics(tool))
