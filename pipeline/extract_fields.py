from google import genai
import sqlite3
from time import sleep

client = genai.Client()

conn = sqlite3.connect("../data/vagas.db")
cursor = conn.cursor()


def get_ai_response(description: str):
    sleep(5)
    try:
        response = client.models.generate_content(
            model="gemma-3-27b-it",
            contents=f"""
        Extraia as informações abaixo da descrição da vaga. 
        Responda APENAS com JSON válido, sem texto adicional.

        Descrição: {description}

        Formato:
        {{
            "stack": ["lista de tecnologias, linguagens e frameworks mencionados"],
            "nivel": "estagio | junior | pleno | senior | nao_informado",
            "modalidade": "remoto | hibrido | presencial | nao_informado",
            "salario": "valor ou nao_informado",
            "area": "backend | frontend | fullstack | dados | devops | suporte | outro"
        }}
        """,
        )
        return response.text.strip().removeprefix("```json").removesuffix("```")
    except Exception as e:
        print(f"Erro na chamada da IA: {e}")


def get_description():

    selectStm = "SELECT description, id FROM jobs WHERE ai_response IS NULL"
    cursor.execute(selectStm)
    rows = cursor.fetchall()

    if not rows:
        print("Nenhuma vaga pendente.")
        return

    for row in rows:
        print(f"Descriçao: {row[0]}")
        response = get_ai_response(row[0])
        insert_ai_response(response, row[1])


def insert_ai_response(response, id):
    insertStm = "UPDATE jobs SET ai_response = ? WHERE id = ?"

    ai_response_data = (response, id)
    print(f"Response: {response}\n ID:{id}")
    try:
        cursor.execute(insertStm, ai_response_data)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")


try:
    get_description()
finally:
    conn.close()
