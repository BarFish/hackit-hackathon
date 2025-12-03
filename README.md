# hackit-hackathon
Group project for timing attacks: Flask website with a delayed password check plus a Python script for hacking the website and for hacking other websites.

בכל שעה נבחרת אות אקראית חדשה, והיא משמשת כאות המפתח בסיסמא שהמשתמש שולח.
כאשר הסיסמא שנשלחת מכילה את האות הזאת לפחות 11 פעמים, המערכת נכנסת למסלול
בדיקה מיוחד שבו הדיליי מאפשר לקבל מידע נוסף.
במסלול זה האלגוריתם בודק רק את האות האחת ששונה מאות המפתח של אותה שעה (אם יש כזאת).
הזמן במסלול זה יהיה מינימלי כאשר התו נכון.
במסלול בדיקה השני (אם זה לא מתקיים) יש דיליי רנדומלי גבוה שהוספנו לו דיליי שמטרתו לבלבל
את מי שמנסה למצוא את אורך הסיסמא.

## To install requirements:
pip install -r requirements.txt
