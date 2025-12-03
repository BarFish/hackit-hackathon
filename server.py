from flask import Flask
from time import sleep
import random
from datetime import datetime

POOL = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
# Alternative smaller pool for testing:
# POOL = 'aopqsAPTU16790'
SECRET_PASSWORD = '6UsP9o'
LONG_PADDING = ' ' * 12

last_day = -1
last_hour = -1
current_letter = ''

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
@app.route('/<string:inPass>', methods=['GET','POST'])
def index(inPass=''):
    return '1' if verify_password(inPass) else '0'


def count_cur_letter(paddedInPassword, cur_letter):
    """
    Counts occurrences of the key letter in the padded password.
    
    :param paddedInPassword: (str) The padded input password.
    :param cur_letter: (char) The key letter to count.
    :return: (int) The index of the differing character if the key letter 
    occurs at least 11 times, otherwise -1.
    """
    count = 0
    diff_index = 0
    for i in range(len(paddedInPassword)):
        if paddedInPassword[i] == cur_letter:
            count += 1
        else:
            diff_index = i
    return diff_index if count >= 11 else -1


def check_hour_change():
    """
    Checks if the hour has changed and updates the current key letter if so.
    """
    global last_day, last_hour, current_letter

    now = datetime.now()
    day = now.day
    hour = now.hour

    if day != last_day or hour != last_hour:
        last_day = day
        last_hour = hour
        last_letter = current_letter
        while current_letter == last_letter:
            current_letter = random.choice(POOL)


def verify_password(inPass):
    """
    Verifies the input password against the secret password with timing delays.
    בכל שעה נבחרת אות אקראית חדשה, והיא משמשת כאות המפתח בסיסמא שהמשתמש שולח.
    כאשר הסיסמא שנשלחת מכילה את האות הזאת לפחות 11 פעמים, המערכת נכנסת למסלול
    בדיקה מיוחד שבו הדיליי מאפשר לקבל מידע נוסף.
    במסלול זה האלגוריתם בודק רק את האות האחת ששונה מאות המפתח של אותה שעה (אם יש כזאת).
    הזמן במסלול זה יהיה מינימלי כאשר התו נכון.
    במסלול בדיקה השני (אם זה לא מתקיים) יש דיליי רנדומלי גבוה שהוספנו לו דיליי שמטרתו לבלבל
    את מי שמנסה למצוא את אורך הסיסמא.
    
    :param inPass: (str) The input password to verify.
    :return: (bool) True if the password is correct, False otherwise.
    """
    check_hour_change()

    delay = 0.0

    paddedInPassword = (LONG_PADDING + inPass)[-len(LONG_PADDING):]
    paddedSecretPassword = (LONG_PADDING + SECRET_PASSWORD)[-len(LONG_PADDING):]

    diff_index = count_cur_letter(paddedInPassword, current_letter)

    if diff_index >= 0:

        for _ in range(11):
            delay += random.uniform(0.2, 0.22)

        if paddedInPassword[diff_index] == paddedSecretPassword[diff_index]:
            delay += random.uniform(0.05, 0.1)
        elif paddedInPassword[diff_index] == current_letter:
            delay += random.uniform(0.13, 0.15)
        else:
            delay += random.uniform(0.28, 0.3)

    else:

        for _ in range(len(paddedInPassword)):
            if len(inPass) < len(SECRET_PASSWORD) - 1:
                delay += random.uniform(0.2, 0.24)
            delay += random.uniform(0.21, 0.3)

    sleep(delay)
    return inPass == SECRET_PASSWORD


if __name__ == "__main__":
    app.run(debug=True)
