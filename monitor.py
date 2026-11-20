import os
import json
import requests
import yfinance as yf
from datetime import datetime
import pytz

# Credenciais do Telegram (puxadas do cofre seguro do GitHub)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Arquivo para salvar o estado dos alertas e controle diário
STATE_FILE = "ultimo_preco.json"

# Sua lista completa e oficial com os limites e a trava de variação
TARGETS = {
    "KLBN4.SA": {"limite_inferior": 3.47, "limite_superior": 3.60, "variacao_min_pct": 1.0},
    "ITSA4.SA": {"limite_inferior": 12.90, "limite_superior": 15.00, "variacao_min_pct": 1.0},
    "BBAS3.SA": {"limite_inferior": 14.00, "limite_superior": 15.00, "variacao_min_pct": 1.0},
    "CXSE3.SA": {"limite_inferior": 20.00, "limite_superior": 22.00, "variacao_min_pct": 1.0},
    "BBDC4.SA": {"limite_inferior": 14.00, "limite_superior": 15.00, "variacao_min_pct": 1.0},
    "CMIG4.SA": {"limite_inferior": 10.00, "limite_superior": 11.00, "variacao_min_pct": 1.0},
    "SAPR4.SA": {"limite_inferior": 5.90, "limite_superior": 6.50, "variacao_min_pct": 1.0},
    "POMO4.SA": {"limite_inferior": 3.50, "limite_superior": 4.00, "variacao_min_pct": 1.0},
    "BBSE3.SA": {"limite_inferior": 36.90, "limite_superior": 38.90, "variacao_min_pct": 1.0},
    "TAEE4.SA": {"limite_inferior": 12.90, "limite_superior": 15.00, "variacao_min_pct": 1.0},
    "BTC-USD": {"limite_inferior": 65000.00, "limite_superior": 75000.00, "variacao_min_pct": 1.5}
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
        print("Erro: Chaves do Telegram não encontradas.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar telegram: {e}")

def enviar_resumo_abertura(agora_br):
    print(f"[{agora_br}] Gerando boletim de abertura do pregão...")
    relatorio = f"🌅 **BOLETIM DE ABERTURA ({agora_br.strftime('%d/%m %H:%M')})** 🌅\n\n"
    
    for ticker in TARGETS.keys():
        try:
            dados = yf.Ticker(ticker).history(period="5d")
            if dados.empty:
                continue
            preco_atual = float(dados['Close'].iloc[-1])
            moeda = "US$" if ticker == "BTC-USD" else "R$"
            relatorio += f"• `{ticker.replace('.SA', '')}`: {moeda} {preco_atual:.2f}\n"
        except Exception as e:
            print(f"Erro ao buscar abertura de {ticker}: {e}")

    send_push_alert(relatorio)

def check_prices():
    fuso_br = pytz.timezone('America/Sao_Paulo')
    print(f"[{datetime.now(fuso_br)}] Iniciando verificação inteligente de preços...")
    estado_anterior = carregar_estado()
    estado_atualizado = estado_anterior.copy()

    for ticker, config in TARGETS.items():
        try:
            dados = yf.Ticker(ticker).history(period="5d")
            if dados.empty:
                continue
            preco_atual = float(dados['Close'].iloc[-1])

            inf = config["limite_inferior"]
            sup = config["limite_superior"]
            variacao_min = config["variacao_min_pct"]

            print(f"{ticker}: R$ {preco_atual:.2f} (Inf: {inf} Sup: {sup})")

            if preco_atual <= inf or preco_atual >= sup:
                tipo_limite = "inferior" if preco_atual <= inf else "superior"
                limite_valor = inf if tipo_limite == "inferior" else sup
                
                chave_estado = f"{ticker}_{tipo_limite}"
                ultimo_preco_alerta = estado_anterior.get(chave_estado)

                deve_alertar = False
                if ultimo_preco_alerta is None:
                    deve_alertar = True
                else:
                    diferenca_pct = abs(preco_atual - ultimo_preco_alerta) / ultimo_preco_alerta * 100
                    if diferenca_pct >= variacao_min:
                        deve_alertar = True

                if deve_alertar:
                    if tipo_limite == "inferior":
                        mensagem = f"🚨 **ALERTA DE QUEDA / OPORTUNIDADE!** O ativo `{ticker}` atingiu o limite inferior de R$ {limite_valor}! Preço atual: R$ {preco_atual:.2f}"
                    else:
                        mensagem = f"📈 **ALERTA DE ALTA / ALVO ATINGIDO!** O ativo `{ticker}` atingiu o limite superior de R$ {limite_valor}! Preço atual: R$ {preco_atual:.2f}"
                    
                    send_push_alert(mensagem)
                    estado_atualizado[chave_estado] = preco_atual

        except Exception as e:
            print(f"Erro ao consultar {ticker}: {e}")

    salvar_estado(estado_atualizado)

def enviar_resumo_fechamento():
    fuso_br = pytz.timezone('America/Sao_Paulo')
    print(f"[{datetime.now(fuso_br)}] Gerando relatório de fechamento do dia...")
    relatorio = "📊 **RESUMO DE FECHAMENTO DO DIA (B3 & BTC)** 📊\n\n"
    
    for ticker in TARGETS.keys():
        try:
            dados = yf.Ticker(ticker).history(period="2d")
            if dados.empty:
                continue
            preco_fechamento = float(dados['Close'].iloc[-1])
            moeda = "US$" if ticker == "BTC-USD" else "R$"
            
            if len(dados) >= 2:
                preco_anterior = float(dados['Close'].iloc[-2])
                var_dia = ((preco_fechamento - preco_anterior) / preco_anterior) * 100
                sinal = "+" if var_dia > 0 else ""
                relatorio += f"• `{ticker.replace('.SA', '')}`: {moeda} {preco_fechamento:.2f} ({sinal}{var_dia:.2f}%)\n"
            else:
                relatorio += f"• `{ticker.replace('.SA', '')}`: {moeda} {preco_fechamento:.2f}\n"
        except Exception as e:
            print(f"Erro ao buscar fechamento de {ticker}: {e}")

    send_push_alert(relatorio)

if __name__ == "__main__":
    fuso_br = pytz.timezone('America/Sao_Paulo')
    agora_br = datetime.now(fuso_br)
    hoje_str = agora_br.strftime('%Y-%m-%d')
    
    # Horário de Brasília: Das 10:00 às 18:59
    if 10 <= agora_br.hour < 19:
        estado = carregar_estado()
        if estado.get("data_abertura") != hoje_str:
            enviar_resumo_abertura(agora_br)
            estado["data_abertura"] = hoje_str
            salvar_estado(estado)
            
        check_prices()
        
    # Horário de Brasília: Das 19:00 às 19:14 (com trava para não repetir no mesmo dia)
    elif agora_br.hour == 19 and 0 <= agora_br.minute < 15:
        estado = carregar_estado()
        if estado.get("data_fechamento") != hoje_str:
            enviar_resumo_fechamento()
            estado["data_fechamento"] = hoje_str
            salvar_estado(estado)
