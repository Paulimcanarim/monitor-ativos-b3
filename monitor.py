import os
import requests
import yfinance as yf
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

TARGETS = {
    "ITSA4.SA": {"limite_inferior": 12.90},
    "BBAS3.SA": {"limite_inferior": 15.00}
}

def send_push_alert(msg):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Erro: Chaves do Telegram não encontradas.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar Telegram: {e}")

def check_prices():
    print(f"[{datetime.now()}] Iniciando verificação de preços...")
    for ticker, config in TARGETS.items():
        try:
            dados = yf.Ticker(ticker).history(period="1d")
            if dados.empty:
                continue
            preco_atual = float(dados['Close'].iloc[-1])
            alvo = config["limite_inferior"]
            
            print(f"{ticker}: R$ {preco_atual:.2f} (Alvo: R$ {alvo:.2f})")
            
            if preco_atual <= alvo:
                mensagem = f"🚨 **ALERTA DE OPORTUNIDADE!**\n\nO ativo **{ticker}** atingiu o seu preço alvo!\n📉 **Preço Atual:** R$ {preco_atual:.2f}\n🎯 **Seu Alvo:** R$ {alvo:.2f}"
                send_push_alert(mensagem)
        except Exception as e:
            print(f"Erro ao consultar {ticker}: {e}")

if __name__ == "__main__":
    check_prices()
