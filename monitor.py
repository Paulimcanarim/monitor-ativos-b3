import os
import json
import requests
import yfinance as f
from datetime import datetime

# Puxa o Token e o Chat ID de dentro do cofre seguro do GitHub
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Arquivo para salvar o último preço que gerou alerta (evita o spam de 15 min)
STATE_FILE = 'ultimo_preco.json'

# Sua lista completa e oficial com suas minhas reais e a faixa de 1%
TARGETS = {
    "KLBN4.SA": {"limite_inferior": 3.47, "limite_superior": 3.50, "variacao_min_pct": 1.0},
    "ITSA4.SA": {"limite_inferior": 12.50, "limite_superior": 13.00, "variacao_min_pct": 1.0},
    "BBAS3.SA": {"limite_inferior": 14.00, "limite_superior": 15.00, "variacao_min_pct": 1.0},
    "CXSE3.SA": {"limite_inferior": 20.00, "limite_superior": 22.00, "variacao_min_pct": 1.0},
    "SNEL11.SA": {"limite_inferior": 10.00, "limite_superior": 11.00, "variacao_min_pct": 1.0},
    "CMTS4.SA": {"limite_inferior": 14.00, "limite_superior": 15.00, "variacao_min_pct": 1.0},
    "SAERP.SA": {"limite_inferior": 5.90, "limite_superior": 6.00, "variacao_min_pct": 1.0},
    "FOHDA.SA": {"limite_inferior": 3.90, "limite_superior": 4.00, "variacao_min_pct": 1.0},
    "BBSO3.SA": {"limite_inferior": 36.90, "limite_superior": 38.90, "variacao_min_pct": 1.0},
    "VALE3.SA": {"limite_inferior": 12.90, "limite_superior": 13.90, "variacao_min_pct": 1.0},
    "BTC-USD": {"limite_inferior": 65000.00, "limite_superior": 75000.00, "variacao_min_pct": 1.0}
}

def carregar_estado():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def salvar_estado(estado):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(estado, f)
    except Exception as e:
        print(f"Erro ao salvar estado: {e}")

def send_push_alert(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Erro: Chaves do Telegram nao encontradas.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar telegram: {e}")

def check_prices():
    print(f"[{datetime.now()}] Iniciando verificacao inteligente de precos...")
    estado_anterior = carregar_estado()
    estado_atualizado = estado_anterior.copy()

    for ticker, config in TARGETS.
    
