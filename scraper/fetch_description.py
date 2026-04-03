import sqlite3
import requests


with sqlite3.connect("../data/vagas.db") as conn:
    try:
        selectStm = """
        SELECT id, title, link, source FROM jobs WHERE description IS NULL;
        """

        cursor = conn.cursor()
        cursor.execute(selectStm)
        rows = cursor.fetchall()

        for row in rows:
            try:
                payload = {"job_url": row[2], "source": row[3]}
                x = requests.post(
                    "http://0.0.0.0:8001/api/scrape", json=payload, timeout=10
                )
                data = x.json()

                if "job_description" not in data or not data["job_description"]:
                    print(f"Resposta inválida para {row[1]}")
                    continue

                description = data["description"]

                insertStm = """
                UPDATE jobs SET description = ? WHERE id = ?
                """

                descriptionData = (description, row[0])
                cursor.execute(insertStm, descriptionData)
                conn.commit()
                print(f"Descrição adicionada para a vaga: {row[1]}")

            except requests.exceptions.Timeout:
                print(f"Timeout ao buscar {row[2]}")
            except requests.exceptions.RequestException as e:
                print(f"Erro na requisição para {row[1]}: {e}")
            except sqlite3.Error as e:
                print(f"Error no banco para {row[1]}: {e}")

    except sqlite3.Error as e:
        print(f"Error {e}")
