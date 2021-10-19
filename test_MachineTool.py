import pytest
from MachineTool import *


def clean_lists():
    MachineTool.mt_list = []
    MachineTool.mt_order = []


def test_start_process_order_end():
    clean_lists()
    machine_tool = MachineTool(0, 0)
    machine_tool.add_detail(100, 2)
    machine_tool.add_detail(50, 1)
    MachineTool.mt_order = MachineTool.mt_list[:]
    machine_tool.start_process()
    machine_tool.start_process()
    machine_tool.start_process()
    assert MachineTool.mt_order == [] \
           and machine_tool.details_list[0].fact_amount == 2 and machine_tool.details_list[1].fact_amount == 1


def test_start_process_order_end_big_amount():
    clean_lists()
    machine_tool = MachineTool(0, 0)
    machine_tool.add_detail(1, 200)
    machine_tool.add_detail(2, 250)
    MachineTool.mt_order = MachineTool.mt_list[:]
    proc = 0
    while True:
        proc += 1
        machine_tool.start_process()
        if machine_tool.details_list[0].fact_amount == 200 and machine_tool.details_list[1].fact_amount == 250:
            break
    assert proc == 450


def test_start_process_swich_detail():
    clean_lists()
    machine_tool = MachineTool(0, 0)
    machine_tool.add_detail(100, 2)
    machine_tool.add_detail(60, 2)
    MachineTool.mt_order = MachineTool.mt_list[:]
    machine_tool.start_process()
    machine_tool.start_process()
    machine_tool.start_process()
    assert machine_tool.process_time_left == 60


def test_update_order():
    clean_lists()
    machine_tool_1 = MachineTool(0, 0)
    machine_tool_1.add_detail(100, 2)
    machine_tool_2 = MachineTool(5000, 5000)
    machine_tool_2.add_detail(50, 2)
    MachineTool.mt_order = MachineTool.mt_list[:]
    machine_tool_1.start_process()
    machine_tool_2.start_process()
    MachineTool.update_order()
    assert MachineTool.mt_order == [machine_tool_2, machine_tool_1]


def test_update_order_with_time():
    clean_lists()
    machine_tool_1 = MachineTool(0, 0)
    machine_tool_1.add_detail(100, 2)
    machine_tool_2 = MachineTool(5000, 5000)
    machine_tool_2.add_detail(50, 2)
    MachineTool.mt_order = MachineTool.mt_list[:]
    machine_tool_1.start_process()
    machine_tool_2.start_process()
    MachineTool.update_order(60)
    assert machine_tool_2.process_time_left == 0 and machine_tool_1.process_time_left == 40


def test_update_order_new_detail_download():
    clean_lists()
    machine_tool_1 = MachineTool(0, 0)
    machine_tool_1.add_detail(100, 1)
    machine_tool_1.add_detail(15, 3)
    machine_tool_2 = MachineTool(5000, 5000)
    machine_tool_2.add_detail(50, 1)
    machine_tool_2.add_detail(25, 2)
    MachineTool.mt_order = MachineTool.mt_list[:]
    MachineTool.mt_order[0].start_process()
    MachineTool.mt_order[0].start_process()
    MachineTool.mt_order[0].start_process()
    MachineTool.mt_order[0].start_process()
    assert MachineTool.mt_order == [machine_tool_1]
