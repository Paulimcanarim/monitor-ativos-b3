import os
import requests
import yfinance as yf
from datetime import datetime

# Credenciais do Telegram
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Sua lista completa de ativos e limites configurados
TARGETS = {
    "KLBN4.SA": {"limite_inferior": 3.47, "limite_superior": 5.00},
    "ITSA4.SA": {"limite_inferior": 10.50, "limite_superior": 12.00},
    "BBAS3.SA": {"limite_inferior": 24.00, "limite_superior": 34.00},
    "CXSE3.SA": {"limite_inferior": 12.00, "limite_superior": 17.00},
    "CMIG4.SA": {"limite_inferior": 10.00, "limite_superior": 15.00},
    "SAPR4.SA": {"limite_inferior": 6.50, "limite_superior": 9.00},
    "MRVE3.SA": {"limite_inferior": 3.50, "limite_superior": 4.00},
    "MYPK3.SA": {"limite_inferior": 16.50, "limite_superior": 22.00},
    "TAEE4.SA": {"limite_inferior": 12.50, "limite_superior": 16.00},
    "BTC-USD": {"limite_inferior": 65000.00, "limite_superior": 95000.00}
}

def send_push_alert(msg):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Erro: Credenciais do Telegram não encontradas.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar telegram: {e}")

def check_prices():
    print(f"[{datetime.now()}] Iniciando verificação de preços...")
    for ticker, config in TARGETS.items():
        try:
            # Corrigido para period='5d' para garantir que traz a cotação real atualizada
            dados = yf.Ticker(ticker).history(period="5d")
            if dados.empty:
                continue
            preco_atual = float(dados['Close'].iloc[-1])

            inf = config["limite_inferior"]
            sup = config["limite_superior"]

            print(f"{ticker}: R$ {preco_atual:.2f} (Inf: {inf} Sup: {sup})")

            if preco_atual <= inf:
                mensagem = f"🚨 **ALERTA DE QUEDA / OPORTUNIDADE!** O ativo `{ticker}` atingiu o limite inferior de R$ {inf}! Preço atual: R$ {preco_atual:.2f}"
                send_push_alert(mensagem)
            elif preco_atual >= sup:
                mensagem = f"📈 **ALERTA DE ALTA / ALVO ATINGIDO!** O ativo `{ticker}` atingiu o limite superior de R$ {sup}! Preço atual: R$ {preco_atual:.2f}"
                send_push_alert(mensagem)

        except Exception as e:
            print(f"Erro ao consultar {ticker}: {e}")

if __name__ == "__main__":
    check_prices()
