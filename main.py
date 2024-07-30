# coding:utf-8

import os
import PySide2


dir_name = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dir_name, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


from guietta import Gui, III, ___, _, C, HSeparator
from PySide2.QtWidgets import QPlainTextEdit, QTableWidget, QTableWidgetItem
from node import Node


def clear_table(control):
    for i in range(control.widgets['table'].rowCount()):
        del_table_row(control, 0)
    return


def add_table_row(control, row, str_0='', str_1='string', str_2='', sheet_name=''):
    control.widgets['table'].insertRow(row)
    item = QTableWidgetItem(str_0)
    control.widgets['table'].setItem(row, 0, item)
    item = QTableWidgetItem(str_1)
    control.widgets['table'].setItem(row, 1, item)
    item = QTableWidgetItem(str_2)
    control.widgets['table'].setItem(row, 2, item)
    item = QTableWidgetItem(sheet_name)
    control.widgets['table'].setItem(row, 3, item)
    return


def add_current_table_row(control, add_dir, str_0='', str_1='string', str_2='', sheet_name=''):
    current_row = control.widgets['table'].currentRow()
    if current_row == -1:
        add_dir = 1
    target_row = current_row + add_dir
    add_table_row(control, target_row, str_0, str_1, str_2, sheet_name)
    return


def del_table_row(control, row):
    control.widgets['table'].removeRow(row)
    return


def del_current_table_row(control):
    current_row = control.widgets['table'].currentRow()
    if current_row == -1:
        current_row = control.widgets['table'].rowCount()-1
    del_table_row(control, current_row)
    return


def resize_table_row(control):
    row_count = int(control.row_count)
    if row_count >= 0:
        clear_table(control)
    for i in range(row_count):
        add_table_row(control, 0)
    return


def generate_insert_table_command(lib_name, flag_into, flag_partition, flag_realtime):
    tmp_str = ''
    if flag_partition is True:
        tmp_str = ' partition(dt=' + (':dt' if flag_realtime is False else '\'${DateUtil.addDays(dt, 1)}\'') + ')'
    return 'insert ' + ('overwrite' if flag_into is False else 'into') + ' table ' + lib_name + tmp_str


def generate_drop_table_command(lib_name):
    return 'drop table if exists ' + lib_name


def generate_create_table_command(lib_name, lib_comment, item_list, flag_partition):
    ret_str = 'create table if not exists ' + lib_name + '\n('
    for item in item_list:
        ret_str += '\n    ' + item[0] + ' ' + item[1] + ' comment ' + item[2] + ','
    ret_str = ret_str[:-1] + '\n) comment ' + lib_comment + '\n'
    if flag_partition is True:
        ret_str += 'partitioned by (dt string)'
    return ret_str


def generate_select_command(item_list):
    ret_str = 'select'
    for item in item_list:
        ret_str += '\n   ' + item[3] + '.' + item[0] + ','
    ret_str = ret_str[:-1] + '\nfrom'
    return ret_str


def quot_str(string):
    return '\'' + str(string) + '\''


def generate_command(control):
    flag_into = control.cb_insert.isChecked()
    flag_partition = control.cb_dt.isChecked()
    flag_realtime = control.cb_realtime.isChecked()
    lib_sheet_name = control.lib_name+'.'+control.sheet_name
    control.line_drop = generate_drop_table_command(lib_sheet_name)
    control.line_insert = generate_insert_table_command(lib_sheet_name, flag_into, flag_partition, flag_realtime)
    lib_comment = quot_str(control.lib_comment)
    item_list = []
    for row in range(control.widgets['table'].rowCount()):
        table_item = control.widgets['table']
        item_0 = table_item.item(row, 0).text()
        item_1 = table_item.item(row, 1).text()
        item_2 = table_item.item(row, 2).text()
        item_3 = table_item.item(row, 3).text()
        if item_0 != '' or item_2 != '':
            item_list.append([item_0, item_1, quot_str(item_2), item_3])
    if item_list:
        create_table_command = generate_create_table_command(lib_sheet_name, lib_comment, item_list, flag_partition)
        control.widgets['txt_output'].setPlainText(create_table_command)

        select_command = generate_select_command(item_list)
        control.widgets['txt_select'].setPlainText(select_command)
    return


def transformation_code_to_table(control):
    sheet_node = Node('root', control.text_code.toPlainText())
    sheet_node.analyse_text()
    word_list = sheet_node.get_word(append_type='list')
    if word_list:
        clear_table(control)
        for index, item in enumerate(word_list):
            print(item)
            add_table_row(control, index, item[0], sheet_name=item[1])
    return


def event_add_table_row(gui, *args):
    add_current_table_row(gui, 0)
    return


def event_add_table_row_after(gui, *args):
    add_current_table_row(gui, 1)
    return


def event_del_table_row(gui, *args):
    del_current_table_row(gui)
    return


def event_resize_table(gui, *args):
    resize_table_row(gui)
    return


def event_generate_command(gui, *args):
    generate_command(gui)
    return


def event_transformation_code(gui, *args):
    transformation_code_to_table(gui)
    return


def event_work(gui, *args):
    transformation_code_to_table(gui)
    generate_command(gui)
    return


def main():
    gui = Gui\
        (
            ['库名', '__lib_name__', ___, ___, '表名', '__sheet_name__', ___, ___, '注释', '__lib_comment__', ___, ___, (C('dt分区'), 'cb_dt'), ___, '行数', '__row_count__', ___, ___, (['重置'],'bt_resize'), ___],
            [(QTableWidget, 'table'), ___, ___, ___, ___, ___, ___, ___, ___,  (QPlainTextEdit, 'text_code'),  ___, ___, ___, ___, ___, ___, ___, ___, ___, ___],
            [III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III],
            [III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III],
            [III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III],
            [(['添加'], 'bt_add'), ___, (['添后'], 'bt_add_after'), ___,(['删除'], 'bt_del'), ___, _, (['生成'], 'bt_create'), ___, _, _, _, _, _, _, _, (['转换'], 'bt_transformation'), ___, (['直接生成'], 'bt_work'), ___],
            [HSeparator],
            ['__line_drop__', ___, ___, ___, ___, ___, ___, ___,  ___, ___, ___, ___, ___, ___, ___, ___, ___, ___, ___, ___],
            ['__line_insert__', ___, ___, ___, ___, ___, ___, ___,  ___, ___, ___, ___, ___, ___, ___, ___, ___, ___, (C('into'), 'cb_insert'), (C('实时'), 'cb_realtime')],
            [(QPlainTextEdit, 'txt_output'), ___, ___, ___, ___, ___, ___, ___, ___, ___, (QPlainTextEdit, 'txt_select'), ___, ___, ___, ___, ___, ___, ___, ___, ___],
            [III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III],
            [III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III],
            [III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III, III],

            title='建表语句自动生成工具'
        )

    gui.widgets['table'].setColumnCount(4)
    gui.widgets['table'].setHorizontalHeaderItem(0, QTableWidgetItem('字段名'))
    gui.widgets['table'].setHorizontalHeaderItem(1, QTableWidgetItem('类型'))
    gui.widgets['table'].setHorizontalHeaderItem(2, QTableWidgetItem('注释'))
    gui.widgets['table'].setHorizontalHeaderItem(3, QTableWidgetItem('表名'))

    gui.widgets['table'].setColumnWidth(0, 100)
    gui.widgets['table'].setColumnWidth(1, 100)
    gui.widgets['table'].setColumnWidth(2, 100)
    gui.widgets['table'].setColumnWidth(3, 70)

    # gui.widgets['table'].setAlternatingRowColors(True)
    # gui.widgets['table'].verticalHeader().setVisible(False)
    gui.widgets['table'].setVerticalScrollBarPolicy(PySide2.QtCore.Qt.ScrollBarAlwaysOn)
    gui.widgets['table'].setStyleSheet("QHeaderView::section{border: 1px solid white}")
    add_table_row(gui, 0)

    gui.bt_add = event_add_table_row
    gui.bt_add_after = event_add_table_row_after
    gui.bt_del = event_del_table_row
    gui.bt_resize = event_resize_table
    gui.bt_create = event_generate_command
    gui.bt_transformation = event_transformation_code
    gui.bt_work = event_work

    gui.cb_dt.setChecked(True)
    # gui.cb_insert.setChecked(True)

    gui.run()
    return


if __name__ == '__main__':
    main()
