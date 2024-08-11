#! /usr/bin/env python3

from modified_paramiko_pkey import KeyDecrpter

from datetime import date
from optparse import OptionParser
from colorama import Fore, Back, Style
from multiprocessing import Pool, Lock, cpu_count
from time import strftime, localtime, time

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
                cracked.append([key_name, word])
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
    keys, cracked_keys = {}, []
    display(':', f"Loading {Back.MAGENTA}{len(data.key)}{Back.RESET} Keys...")
    for key_name in data.key:
        try:
            with open(key_name, 'r') as file:
                keys[key_name] = file.readlines()
            display(':', f"\tLoaded Key => {Back.MAGENTA}{key_name}{Back.RESET}")
        except FileNotFoundError:
            display('-', f"File {Back.MAGENTA}{key_name}{Back.RESET} not Found!")
        except Exception as error:
            display('-', f"Error while loading File {Back.MAGENTA}{key_name}{Back.RESET} => {Back.YELLOW}{error}{Back.RESET}")
    total_keys = len(keys)
    display('+', f"Loaded {Back.MAGENTA}{total_keys}{Back.RESET} Keys!")
    wordlists = data.load.split(',')
    display(':', f"Total Wordlists = {Back.MAGENTA}{len(wordlists)}{Back.RESET}")
    for file_index, wordlist in enumerate(wordlists):
        try:
            display(':', f"Loading File {Back.MAGENTA}{file_index+1}/{len(wordlists)} => {wordlist}{Back.RESET}", start='\n')
            with open(wordlist, 'rb') as file:
                words = [word.replace('\r', '') for word in file.read().decode(errors="ignore").split('\n')]
        except FileNotFoundError:
            display('-', f"File {Back.YELLOW}{wordlist}{Back.RESET} not found!")
            continue
        except MemoryError:
            display('-', f"File {Back.MAGENTA}{wordlist}{Back.RESET} too big to load!")
            display(':', f"Loading {Back.MAGENTA}{data.number_of_words}{Back.RESET} words at once from the file.")
            with open(wordlist, 'rb') as file:
                done = False
                words_loaded = 0
                current_file_cracked_keys = 0
                while not done:
                    current_words_loaded = 0
                    words = []
                    t1 = time()
                    while len(words) < data.number_of_words and not done:
                        word = file.readline().decode(errors="ignore")
                        if word == '':
                            done = True
                        words.append(word.replace('\n', '').replace('\r', ''))
                        current_words_loaded += 1
                    words_loaded += current_words_loaded
                    t2 = time()
                    display('+', f"Loaded {Back.MAGENTA}{data.number_of_words}{Back.RESET} words from the file.")
                    display(':', f"\tTime Taken = {Back.MAGENTA}{t2-t1:.2f} seconds{Back.RESET}")
                    display(':', f"\tRate = {Back.MAGENTA}{current_words_loaded/(t2-t1):.2f} words/second{Back.RESET}")
                    display(':', "Decrypting...")
                    t1 = time()
                    current_cracked_keys = crackKeysHandler(words, keys)
                    cracked_keys.extend(current_cracked_keys)
                    for cracked_key, password in cracked_keys:
                        if cracked_key in keys.keys():
                            keys.pop(cracked_key)
                    t2 = time()
                    display('+', "Current Batch Done", start='\n')
                    display(':', f"\tTime Taken = {Back.MAGENTA}{t2-t1:.2f} seconds{Back.RESET}")
                    display(':', f"\tRate = {Back.MAGENTA}{current_words_loaded/(t2-t1):.2f} words/second{Back.RESET}")
                    current_cracked_keys = len(current_cracked_keys)
                    current_file_cracked_keys += current_cracked_keys
                    display(':', f"\tKeys Cracked from Current Batch = {Back.MAGENTA}{current_cracked_keys}{Back.RESET}")
                    display(':', f"\tKeys Cracked from Current File  = {Back.MAGENTA}{current_file_cracked_keys}{Back.RESET}")
                display(':', f"\tKeys Cracked from Current file = {Back.MAGENTA}{current_file_cracked_keys}{Back.RESET}")
                display(':', f"Total Cracked Keys = {Back.MAGENTA}{len(cracked_keys)}{Back.RESET}")
                if len(cracked_keys) == total_keys:
                    display('+', f"Done Cracking all the Keys!")
                    break
            continue
        except:
            display('-', f"Error while reading File {Back.YELLOW}{wordlist}{Back.RESET}")
            continue
        display('+', f"Words Loaded = {Back.MAGENTA}{len(words)}{Back.RESET}")
        display(':', f"Decrypting...")
        t1 = time()
        current_cracked_keys = crackKeysHandler(words, keys)
        cracked_keys.extend(current_cracked_keys)
        for cracked_key, password in cracked_keys:
            if cracked_key in keys.keys():
                keys.pop(cracked_key)
        t2 = time()
        display(':', f"\tTime Taken = {Back.MAGENTA}{t2-t1:.2f} seconds{Back.RESET}")
        display(':', f"\tRate = {Back.MAGENTA}{len(words)/(t2-t1):.2f} words/second{Back.RESET}")
        current_cracked_keys = len(current_cracked_keys)
        display(':', f"\tKeys Cracked from Current file = {Back.MAGENTA}{current_cracked_keys}{Back.RESET}")
        display(':', f"Total Cracked Keys = {Back.MAGENTA}{len(cracked_keys)}{Back.RESET}")
        if len(cracked_keys) == total_keys:
            display('+', f"Done Cracking all the Keys!")
            break
    print()
    print('\n'.join([f"{Fore.CYAN}{key_path}{Fore.RESET} => {Fore.GREEN}{password}{Fore.RESET}" for key_path, password in cracked_keys]))
    display(':', f"Total Keys Loaded = {Back.MAGENTA}{total_keys}{Back.RESET}", start='\n')
    display(':', f"Total Keys Cracked = {Back.MAGENTA}{len(cracked_keys)}{Back.RESET}")
    display(':', f"Success Rate = {Back.MAGENTA}{len(cracked_keys)/total_keys*100:.2f}%{Back.RESET}")