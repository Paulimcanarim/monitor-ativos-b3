import os
import requests
import yfinance as yf
from datetime import datetime

# Credenciais do Telegram
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Sua lista completa de ativos e limites configurados
TARGETS = {
    "KLBN4.SA": {"limite_inferior": 3.47, "limite_superior": 3.60},
    "ITSA4.SA": {"limite_inferior": 12.90, "limite_superior": 15.00},
    "BBAS3.SA": {"limite_inferior": 14.00, "limite_superior": 15.00},
    "CXSE3.SA": {"limite_inferior": 20.00, "limite_superior": 22.00},
    "BBDC4.SA": {"limite_inferior": 14.00, "limite_superior": 15.00},
    "CMIG4.SA": {"limite_inferior": 10.00, "limite_superior": 11.00},
    "SAPR4.SA": {"limite_inferior": 5.90, "limite_superior": 6.50},
    "POMO4.SA": {"limite_inferior": 3.50, "limite_superior": 4.00},
    "BBSE3.SA": {"limite_inferior": 36.90, "limite_superior": 38.90},
    "TAEE4.SA": {"limite_inferior": 12.90, "limite_superior": 15.00},
    "BTC-USD": {"limite_inferior": 70000.00, "limite_superior": 75000.00}
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
            
            inf = config["limite_inferior"]
            sup = config["limite_superior"]
            
            print(f"{ticker}: R$ {preco_atual:.2f} (Inf: {inf} | Sup: {sup})")
            
            if preco_atual <= inf:
                mensagem = f"🚨 **ALERTA DE QUEDA / OPORTUNIDADE!**\n\nO ativo **{ticker}** atingiu o limite inferior!\n📉 **Preço Atual:** R$ {preco_atual:.2f}\n🎯 **Seu Limite:** R$ {inf:.2f}"
                send_push_alert(mensagem)
            elif preco_atual >= sup:
                mensagem = f"🚀 **ALERTA DE ALTA / ALVO ATINGIDO!**\n\nO ativo **{ticker}** atingiu o limite superior!\n📈 **Preço Atual:** R$ {preco_atual:.2f}\n🎯 **Seu Limite:** R$ {sup:.2f}"
                send_push_alert(mensagem)
                
        except Exception as e:
            print(f"Erro ao consultar {ticker}: {e}")

if __name__ == "__main__":
    check_prices()
   
