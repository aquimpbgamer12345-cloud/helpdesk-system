import pyodbc
import random
from datetime import datetime, timedelta

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=(localdb)\\MSSQLLocalDB;'
    'DATABASE=HelpDesk_TI;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

descriptions = [
    'Tela piscando', 'Teclado não funciona', 'Sem som',
    'Impressora não encontrada', 'Computador lento', 'Email não sincronizando',
    'VPN desconectando', 'Falha na atualização do sistema', 'USB não reconhecido',
    'Problema de resolução do monitor', 'Computador não liga', 'Sem acesso à internet',
    'Mouse com defeito', 'Senha bloqueada', 'Impressora offline'
]

status_list = ['Fechado', 'Fechado', 'Fechado', 'Em Andamento', 'Aberto']
priority_list = ['Baixa', 'Média', 'Alta']

print("Inserindo 30 novos atendimentos distribuídos em 2024, 2025 e 2026...")

for ano in [2024, 2025, 2026]:
    for i in range(10):
        user_id = random.randint(1, 5)
        category_id = random.randint(1, 5)
        status = random.choice(status_list)
        priority = random.choice(priority_list)
        description = random.choice(descriptions)

        mes = random.randint(1, 12)
        dia = random.randint(1, 28)
        hora = random.randint(8, 18)
        opened_at = datetime(ano, mes, dia, hora, 0, 0)
        closed_at = opened_at + timedelta(hours=random.randint(1, 48)) if status == 'Fechado' else None

        cursor.execute("""
            INSERT INTO Tickets (user_id, category_id, description, status, priority, opened_at, closed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, user_id, category_id, description, status, priority, opened_at, closed_at)

conn.commit()
print("30 atendimentos inseridos com sucesso!")

cursor.execute("""
    SELECT YEAR(opened_at) as ano, COUNT(*) as total
    FROM Tickets
    GROUP BY YEAR(opened_at)
    ORDER BY ano
""")

print("\nResumo por ano:")
for row in cursor.fetchall():
    print(f"  {row.ano}: {row.total} atendimentos")

cursor.close()
conn.close()
