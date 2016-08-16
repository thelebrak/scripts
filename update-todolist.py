#!/usr/bin/env python3

import argparse
import os
import re
import datetime
from collections import OrderedDict

"""
    todo-update
    Python script to automatize my personal todo list
    My todolist are written in markdown format. 
    This is an example of the format used

            # To do list
            ## Week 31 - 9/8 -> 15/8
            * Clean my room
            * Call grand-parents

            ## Week 30 -> 25/7 -> 31/7
            * Finish homework
            * Write documentation -> DONE

"""

TODOLIST = 'todolist.md'
README = 'README.md'

def iso_to_gregorian(iso_year, iso_week, iso_day):
    """
        As 4th January is always in the first week on the current year, this day is used
        to determine a date from its week number, the year, and the day (monday..sunday)
        For example, iso_to_gregorian(2016, 21, 1) returns datetime.date(2016, 5, 23)
    """
    jan4 = datetime.date(iso_year, 1, 4)
    start = jan4 - datetime.timedelta(days=jan4.isoweekday()-1)
    return start + datetime.timedelta(weeks=iso_week-1, days=iso_day-1)

def get_week(week_number=None):
    """
        Get week_number and returns information to construct week line and week summary
        If week_number is None, it uses the actual week number
        Returns:
            week_number: Current week number -> int
            start_month : -> str
            start_day : -> str
            end_month : -> str
            end_day : -> str
    """
    today = datetime.date.today()
    year = today.year
    if week_number == None:
        week_number = today.isocalendar()[1]
    start_week = iso_to_gregorian(year, week_number, 1)
    end_week = iso_to_gregorian(year, week_number, 7)

    start_month = format_number(start_week.month)
    start_day = format_number(start_week.day)
    end_month = format_number(end_week.month)
    end_day = format_number(end_week.day)

    return week_number, start_month, start_day, end_month, end_day

def format_number(number):
    """
        Takes an integer, and add '0' if there is only one digit 
        Input : 8 -> int
        Output : '08' -> str
    """
    nb = str(number)
    if len(nb) == 1:
        nb = '0'+nb
    return nb

def get_week_line(week_number=None):
    """
        Return this line
        ## Week week_number - 09/08 -> 15/08\n

        if week_number is None, it uses the actual week_number
    """
    week_nb, s_month, s_day, e_month, e_day = get_week(week_number)

    line = "## Week {} - {}/{} -> {}/{}\n".format(week_nb, 
                                                    s_day, 
                                                    s_month,
                                                    e_day,
                                                    e_month)
    return line

def get_week_summary(percentage, week_number=None):
    """
        Return this line : 
        * [Week week_number](https://gitlab.com/Nairwolf/ToDoList/blob/master/todolist.md#
            week-31-0908-1508) : percentage%\n

        If week_number is None, it uses the actual week_number
    """
    week_nb, s_month, s_day, e_month, e_day = get_week(week_number)

    url = "https://gitlab.com/Nairwolf/ToDoList/blob/master/todolist.md"
    week_summary = "* [Week {}](".format(week_nb)
    
    week_summary += url+"#week-{}-{}{}-{}{})".format(week_nb, 
                                                    s_day, s_month,
                                                    e_day, e_month)

    week_summary += " : {}%\n".format(percentage)
    return week_summary

def parse_todolist(lines):
    """
        Parse list of lines of the todolist.md file. 
        Return a dictionnary with 'week_number' as key, 
        and percentage of tasks done as value.
    """
    regex = re.compile(r'Week (\d\d?)')
    dtasks = {}
    new_lines = []
    
    for l in lines:
        new_l = l
        if l.startswith('##'):
            mo = regex.search(l)
            week_number = int(mo.group(1))
            dtasks[week_number] = 0
            nb_tasks = 0
            tasks_done = 0

            # Verify current week_line and correct it
            new_line = get_week_line(week_number)
            if l.rstrip() != new_line.rstrip():
                new_l = new_line

        if l.startswith('*'):
            nb_tasks += 1
            if l.rfind('DONE') != -1:
                tasks_done += 1
            try:
                percentage = round( (tasks_done / nb_tasks) * 100 )
            except ZeroDivisionError:
                percentage = 0
            dtasks[week_number] = percentage

        new_lines.append(new_l)

    return dtasks, new_lines

def update_todolist():
    """
        Open and read 'todolist.md', parse its lines, verify its information and update 
        it. If the current week is not present, this function will be add it.

        Return a dict with week_number as key and percentage_tasks_done as value
    """
    with open(TODOLIST, 'r') as f:
        lines = f.readlines()

    dtasks, new_lines = parse_todolist(lines)

    new_week = get_week_line()
    if new_lines[1].rstrip() != new_week.rstrip():
        new_lines[0] += new_week+'\n'
    
    with open(TODOLIST, 'w') as f:
        f.write(''.join(new_lines))

    return dtasks

def update_readme(percentages):
    """
        This function write README.md from scratch as percentage of 
        tasks done by weeks is known. 
    """
    od = OrderedDict(reversed(sorted(percentages.items())))

    lines = ['# To do list\n\n', '## Weeks\n\n']

    for week, percentage in od.items():
        line = get_week_summary(percentage, week)
        lines.append(line)

    actual_week = get_week_summary(0)
    if lines[2].rstrip() != actual_week.rstrip():
        lines[1] += actual_week

    with open(README, 'w') as f:
        f.write(''.join(lines))

def verify_content():
    """
        Reads todolist.md and verifies if dates are correctly written and correct 
        them if it's not the case.
    """
    with open(TODOLIST, 'r') as f:
        lines = f.readlines()

    regex = re.compile(r'Week (\d\d?)')
    corrected_lines = []
    need_rewrite = False

    for l in lines:
        new_line = l
        if l.startswith('##'):
            mo = regex.search(l)
            week_number = int(mo.group(1))

            # Verify current week_line and correct it
            line_ref = get_week_line(week_number)
            if l.rstrip() != line_ref.rstrip():
                new_line = line_ref
                need_rewrite = True

        corrected_lines.append(new_line)

    if need_rewrite:
        with open(TODOLIST, 'w') as f:
            f.write(''.join(corrected_lines))

def check_input():
    """
        Verify existence of 'todolist.md' and 'README.md'. The program will stop if 
        these files are not present
    """
    if not os.path.isfile(TODOLIST):
        print("Error: '{}' is not found".format(TODOLIST))
        quit()

    if not os.path.isfile(README):
        print("Error: '{}' is not found".format(README))
        quit()

if __name__ == '__main__':
    check_input()
    verify_content()
    percentages = update_todolist()
    update_readme(percentages)
