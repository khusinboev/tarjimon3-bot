import sqlite3
from pathlib import Path

def clean_html_tags():
    conn = sqlite3.connect("../src/database/dictionary.db")
    cursor = conn.cursor()

    # eng ustunidagi barcha ma'lumotlarni olish
    cursor.execute("SELECT rowid, uzb FROM eng_uzb")
    rows = cursor.fetchall()

    for row in rows:
        rowid, text = row
        if "<br>" in text:
            cleaned_text = text.replace("<br>", " ")  # <br> ni bo'sh joy bilan almashtiramiz
            cursor.execute("UPDATE eng_uzb SET uzb = ? WHERE rowid = ?", (cleaned_text, rowid))

    conn.commit()
    conn.close()
    print("Baza muvaffaqiyatli yangilandi!")


clean_html_tags()
