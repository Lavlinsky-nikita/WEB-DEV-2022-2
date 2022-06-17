# -*- coding: utf-8 -*-
"""
Задание 7.2a

Сделать копию скрипта задания 7.2.

Дополнить скрипт: Скрипт не должен выводить на стандартрый поток вывода команды,
в которых содержатся слова из списка ignore.

При этом скрипт также не должен выводить строки, которые начинаются на !.

Проверить работу скрипта на конфигурационном файле config_sw1.txt.
Имя файла передается как аргумент скрипту.

Ограничение: Все задания надо выполнять используя только пройденные темы.

"""

ignore = ["duplex", "alias", "configuration"]

file_name = "config_sw1.txt"

with open(file_name) as f:
    for line in f:
        word_from_file = line.split()
        word_from_file_ingnore = set(word_from_file) & set(ignore)
        if not line.startswith("!") and not word_from_file_ingnore:
            print(line.rstrip())