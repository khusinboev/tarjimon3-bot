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


def tilmoch(text):
    api = "https://iapi.glosbe.com/iapi3/similar/similarPhrasesMany?p=qalaysan&l1=en&l2=uz&removeDuplicates=true&searchCriteria=WORDLIST-ALPHABETICALLY-2-s%3BPREFIX-PRIORITY-2-s%3BTRANSLITERATED-PRIORITY-2-s%3BFUZZY-PRIORITY-2-s%3BWORDLIST-ALPHABETICALLY-2-r%3BPREFIX-PRIORITY-2-r%3BTRANSLITERATED-PRIORITY-2-r%3BFUZZY-PRIORITY-2-r&env=en"
