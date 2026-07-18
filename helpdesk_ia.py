import pyodbc
import anthropic
from datetime import datetime

# ── Conexão com o banco de dados ──────────────────────────────────────────────
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=(localdb)\\MSSQLLocalDB;'
    'DATABASE=HelpDesk_TI;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

# ── Cliente da API do Claude (Anthropic) ──────────────────────────────────────
client = anthropic.Anthropic(
    api_key= "Sua API key aqui"
)

def sugerir_solucao(descricao: str, prioridade: str, categoria: str) -> str:
    """
    Envia a descrição do chamado para o Claude e retorna uma sugestão de solução.
    """
    prompt = f"""Você é um técnico de suporte de TI experiente.
Um usuário abriu um chamado com as seguintes informações:

- Descrição do problema: {descricao}
- Prioridade: {prioridade}
- Categoria: {categoria}

Forneça uma sugestão de solução clara, objetiva e em português,
com no máximo 3 passos práticos para resolver o problema."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return message.content[0].text


def processar_chamados_abertos():
    """
    Busca chamados com status 'Aberto' e sugere soluções usando IA.
    """
    cursor.execute("""
        SELECT 
            t.ticket_id,
            t.description,
            t.priority,
            t.opened_at,
            c.description AS categoria
        FROM Tickets t
        LEFT JOIN Categories c ON t.category_id = c.category_id
        WHERE t.status = 'Aberto'
        ORDER BY 
            CASE t.priority 
                WHEN 'Alta' THEN 1 
                WHEN 'Média' THEN 2 
                WHEN 'Baixa' THEN 3 
            END
    """)

    chamados = cursor.fetchall()

    if not chamados:
        print("Nenhum chamado aberto encontrado.")
        return

    print(f"\n{'='*60}")
    print(f"  SISTEMA DE HELPDESK COM IA — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}")
    print(f"  {len(chamados)} chamado(s) aberto(s) encontrado(s)\n")

    for chamado in chamados:
        ticket_id  = chamado.ticket_id
        descricao  = chamado.description
        prioridade = chamado.priority
        categoria  = chamado.categoria or "Geral"
        aberto_em  = chamado.opened_at.strftime('%d/%m/%Y %H:%M')

        print(f"{'─'*60}")
        print(f"  🎫 Ticket #{ticket_id}  |  Prioridade: {prioridade}  |  Aberto em: {aberto_em}")
        print(f"  📋 Problema: {descricao}")
        print(f"  📁 Categoria: {categoria}")
        print(f"\n  🤖 Sugestão de solução (Claude AI):")

        try:
            solucao = sugerir_solucao(descricao, prioridade, categoria)
            # Indenta cada linha da resposta
            for linha in solucao.strip().split('\n'):
                print(f"     {linha}")
        except Exception as e:
            print(f"     ⚠️  Erro ao consultar IA: {e}")

        print()

    print(f"{'='*60}")
    print("  Processamento concluído!")
    print(f"{'='*60}\n")


def resumo_chamados():
    """
    Exibe um resumo geral dos chamados no banco.
    """
    cursor.execute("""
        SELECT status, COUNT(*) as total
        FROM Tickets
        GROUP BY status
        ORDER BY total DESC
    """)

    print("\n📊 Resumo geral dos chamados:")
    for row in cursor.fetchall():
        print(f"   {row.status}: {row.total}")


# ── Execução principal ────────────────────────────────────────────────────────
if __name__ == "__main__":
    resumo_chamados()
    processar_chamados_abertos()

    cursor.close()
    conn.close()
