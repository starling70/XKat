# handler.py
from pathlib import Path
import shutil
import sqlite3


def process_files():
    db_path = Path("/home/os/XKat/BASE/xfiles.db")
    
    if not db_path.exists():
        print(f"Помилка: Файл бази даних не знайдено за шляхом {db_path}")
        return

    # Підключення до бази
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Вибираємо всі записи, де статус 6 або 8
    cursor.execute(
        "SELECT idfile, curpath, oldnextpath, statusfile FROM xfiles WHERE statusfile IN (6, 8)"
    )
    rows = cursor.fetchall()

    if not rows:
        print("Немає файлів для обробки (статуси 6 та 8 відсутні).")
        conn.close()
        return

    print(f"Знайдено записів для обробки: {len(rows)}\n")

    for row in rows:
        idfile, curpath_str, oldnextpath_str, statusfile = row
        cur_path = Path(curpath_str) if curpath_str else None

        # -------------------------------------------------------------
        # ОБРОБКА СТАТУСУ 8: Видалення файлу та запису з бази
        # -------------------------------------------------------------
        if statusfile == 8:
            print(f"[ВИДАЛЕННЯ] id={idfile}")
            print(f"  Файл: {cur_path}")
            
            try:
                if cur_path and cur_path.exists():
                    cur_path.unlink()
                    print("  -> Файл успішно видалено з диска.")
                else:
                    print("  -> Увага: Файл на диску не знайдено (пропускаємо видалення файлу).")

                # Видаляємо рядок із бази
                cursor.execute("DELETE FROM xfiles WHERE idfile = ?", (idfile,))
                conn.commit()
                print("  -> Запис видалено з бази даних.\n")
            except Exception as e:
                print(f"  -> ПОМИЛКА при видаленні: {e}\n")

        # -------------------------------------------------------------
        # ОБРОБКА СТАТУСУ 6: Переміщення / перейменування та скидання статусу в 0
        # -------------------------------------------------------------
        elif statusfile == 6:
            next_path = Path(oldnextpath_str) if oldnextpath_str else None
            
            print(f"[ПЕРЕМІЩЕННЯ] id={idfile}")
            print(f"  З:   {cur_path}")
            print(f"  До:  {next_path}")

            if not cur_path or not cur_path.exists():
                print("  -> ПОМИЛКА: Вихідний файл не існує на диску! Пропускаємо.\n")
                continue

            if not next_path:
                print("  -> ПОМИЛКА: Поле oldnextpath порожнє! Пропускаємо.\n")
                continue

            try:
                # Гарантуємо, що цільова директорія існує (якщо це переміщення в іншу папку)
                next_path.parent.mkdir(parents=True, exist_ok=True)

                # Переміщуємо / перейменовуємо файл на дискі
                shutil.move(str(cur_path), str(next_path))
                print("  -> Файл успішно переміщено/перейменовано на дискі.")

                # Оновлюємо базу: 
                # 1. curpath стає новим шляхом (next_path)
                # 2. oldnextpath очищається (NULL)
                # 3. statusfile стає 0
                cursor.execute(
                    """
                    UPDATE xfiles 
                    SET curpath = ?, oldnextpath = NULL, statusfile = 0 
                    WHERE idfile = ?
                """,
                    (str(next_path), idfile),
                )
                conn.commit()
                print("  -> Базу оновлено: статус встановлено в 0, шлях оновлено.\n")
            except Exception as e:
                print(f"  -> ПОМИЛКА при переміщенні: {e}\n")

    conn.close()
    print("Обробку всіх завдань завершено.")


if __name__ == "__main__":
    process_files()