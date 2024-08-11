#! /usr/bin/env python3

from modified_paramiko_pkey import KeyDecrpter

from datetime import date
from optparse import OptionParser
from colorama import Fore, Back, Style
from multiprocessing import Pool, Lock, cpu_count
from time import strftime, localtime

status_color = {
    '+': Fore.GREEN,
    '-': Fore.RED,
    '*': Fore.YELLOW,
    ':': Fore.CYAN,
    ' ': Fore.WHITE
}

lock = Lock()
thread_count = cpu_count()

number_of_words = 100000000

def display(status, data, start='', end='\n'):
    print(f"{start}{status_color[status]}[{status}] {Fore.BLUE}[{date.today()} {strftime('%H:%M:%S', localtime())}] {status_color[status]}{Style.BRIGHT}{data}{Fore.RESET}{Style.RESET_ALL}", end=end)

def get_arguments(*args):
    parser = OptionParser()
    for arg in args:
        parser.add_option(arg[0], arg[1], dest=arg[2], help=arg[3])
    return parser.parse_args()[0]

def crackKeys(words, keys):
    cracked = []
    for word in words:
        for key_name, key_lines in keys.items():
            try:
                KeyDecrpter(lines=key_lines, password=word)
                cracked.append(key_name)
            except:
                pass
    return cracked
def crackKeysHandler(words, keys):
    cracked_keys = []
    threads = []
    pool = Pool(thread_count)
    word_count = len(words)
    word_divisions = [words[group*word_count//thread_count: (group+1)*word_count//thread_count] for group in range(thread_count)]
    for word_division in word_divisions:
        threads.append(pool.apply_async(crackKeys, (word_division, keys)))
    for thread in threads:
        cracked_keys.extend(thread.get())
    pool.close()
    pool.join()
    return cracked_keys

if __name__ == "__main__":
    data = get_arguments(('-l', "--load", "load", "List of Wordlists (seperated by ',')"),
                         ('-k', "--key", "key", "Path to Private Key Files (seperated by ',')"),
                         ('-c', "--count", "number_of_words", f"Number of Words to load from a file at one time if the file is large enough that it can't be read at once (Default={number_of_words})"),
                         ('-w', "--write", "write", "Name of the File for the data to be dumped (default=current data and time)"),)
    if not data.key:
        display('-', "Please provide Private Key Files")
        exit(0)
    else:
        data.key = data.key.split(',')
    if not data.load:
        display('-', "Please specify Wordlists to Load!")
        exit(0)
    if not data.number_of_words:
        data.number_of_words = number_of_words
    else:
        data.number_of_words = int(data.number_of_words)
    if not data.write:
        data.write = f"{date.today()} {strftime('%H_%M_%S', localtime())}"