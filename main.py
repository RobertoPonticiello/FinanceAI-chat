from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from openai import OpenAI
import yfinance as yf
import json
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Initialize OpenAI ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class PromptRequest(BaseModel):
    prompt: str

app = FastAPI(
    title="Financial Data API",
    description="API per l'analisi di dati finanziari con supporto per linguaggio naturale",
    version="1.0.0"
)

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione, specifica i domini consentiti
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Finance functions (all JSON-serializable) ---
def get_return(ticker, period):
    """Calcola il rendimento percentuale di un ticker per un periodo specifico"""
    try:
        data = yf.download(ticker, period=period, progress=False)
        if data.empty or "Close" not in data:
            return None
        start_price = data["Close"].iloc[0]
        end_price = data["Close"].iloc[-1]
        return float(round((end_price - start_price) / start_price * 100, 2))
    except Exception:
        return None

def get_volatility(ticker, period):
    """Calcola la volatilità annualizzata di un ticker per un periodo specifico"""
    try:
        data = yf.download(ticker, period=period, progress=False)
        if data.empty or "Close" not in data:
            return None
        daily_returns = data["Close"].pct_change().dropna()
        vol = daily_returns.std() * (252 ** 0.5)
        return float(round(vol * 100, 2))
    except Exception:
        return None

def get_max_min(ticker, period):
    """Ottiene i prezzi massimo e minimo di un ticker per un periodo specifico"""
    try:
        data = yf.download(ticker, period=period, progress=False)
        if data.empty or "Close" not in data:
            return None
        return {
            "max": float(round(data["Close"].max(), 2)),
            "min": float(round(data["Close"].min(), 2))
        }
    except Exception:
        return None

def get_fundamentals(ticker):
    """Ottiene i dati fondamentali di un ticker"""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        return {
            "longName": info.get("longName"),
            "marketCap": float(info.get("marketCap")) if info.get("marketCap") else None,
            "peRatio": float(info.get("trailingPE")) if info.get("trailingPE") else None,
            "eps": float(info.get("trailingEps")) if info.get("trailingEps") else None,
            "dividendYield": float(info.get("dividendYield")) if info.get("dividendYield") else None,
            "debtToEquity": float(info.get("debtToEquity")) if info.get("debtToEquity") else None,
        }
    except Exception:
        return None

def compare_returns(tickers: List[str], period: str):
    """Confronta i rendimenti di più ticker per un periodo specifico"""
    performances = {}
    for t in tickers:
        r = get_return(t, period)
        if r is not None:
            performances[t] = r
    if not performances:
        return {"error": "No data available for tickers"}
    best_ticker = max(performances, key=lambda k: performances[k])
    return {
        "best_ticker": best_ticker,
        "best_return": performances[best_ticker],
        "all_returns": performances
    }

def compare_volatility(tickers: List[str], period: str):
    """Confronta la volatilità di più ticker per un periodo specifico"""
    volatilities = {}
    for t in tickers:
        vol = get_volatility(t, period)
        if vol is not None:
            volatilities[t] = vol
    
    if not volatilities:
        return {"error": "No volatility data available for tickers"}
    
    # Trova il ticker con la volatilità più bassa (meno rischioso)
    least_volatile = min(volatilities, key=lambda k: volatilities[k])
    # Trova il ticker con la volatilità più alta (più rischioso)
    most_volatile = max(volatilities, key=lambda k: volatilities[k])
    
    return {
        "least_volatile": least_volatile,
        "least_volatility": volatilities[least_volatile],
        "most_volatile": most_volatile,
        "most_volatility": volatilities[most_volatile],
        "all_volatilities": volatilities
    }

def compare_fundamentals(tickers: List[str]):
    """Confronta i fondamentali di più ticker"""
    fundamentals_data = {}
    for t in tickers:
        fund = get_fundamentals(t)
        if fund is not None:
            fundamentals_data[t] = fund
    
    if not fundamentals_data:
        return {"error": "No fundamentals data available for tickers"}
    
    # Analisi comparativa
    comparison = {
        "all_fundamentals": fundamentals_data,
        "analysis": {}
    }
    
    # Confronto Market Cap
    market_caps = {t: data.get("marketCap") for t, data in fundamentals_data.items() 
                   if data.get("marketCap") is not None}
    if market_caps:
        largest_market_cap = max(market_caps, key=lambda k: market_caps[k])
        comparison["analysis"]["largest_market_cap"] = {
            "ticker": largest_market_cap,
            "value": market_caps[largest_market_cap]
        }
    
    # Confronto P/E Ratio (più basso è meglio)
    pe_ratios = {t: data.get("peRatio") for t, data in fundamentals_data.items() 
                 if data.get("peRatio") is not None and data.get("peRatio") > 0}
    if pe_ratios:
        best_pe = min(pe_ratios, key=lambda k: pe_ratios[k])
        comparison["analysis"]["best_pe_ratio"] = {
            "ticker": best_pe,
            "value": pe_ratios[best_pe]
        }
    
    # Confronto Dividend Yield (più alto è meglio)
    dividend_yields = {t: data.get("dividendYield") for t, data in fundamentals_data.items() 
                       if data.get("dividendYield") is not None and data.get("dividendYield") > 0}
    if dividend_yields:
        highest_dividend = max(dividend_yields, key=lambda k: dividend_yields[k])
        comparison["analysis"]["highest_dividend_yield"] = {
            "ticker": highest_dividend,
            "value": dividend_yields[highest_dividend]
        }
    
    # Confronto Debt-to-Equity (più basso è meglio)
    debt_equity = {t: data.get("debtToEquity") for t, data in fundamentals_data.items() 
                   if data.get("debtToEquity") is not None and data.get("debtToEquity") > 0}
    if debt_equity:
        lowest_debt = min(debt_equity, key=lambda k: debt_equity[k])
        comparison["analysis"]["lowest_debt_to_equity"] = {
            "ticker": lowest_debt,
            "value": debt_equity[lowest_debt]
        }
    
    return comparison

def compare_max_min(tickers: List[str], period: str):
    """Confronta i massimi e minimi di più ticker per un periodo specifico"""
    max_min_data = {}
    for t in tickers:
        data = get_max_min(t, period)
        if data is not None:
            max_min_data[t] = data
    
    if not max_min_data:
        return {"error": "No max/min data available for tickers"}
    
    # Trova il massimo assoluto e il minimo assoluto
    all_maxes = {t: data["max"] for t, data in max_min_data.items()}
    all_mins = {t: data["min"] for t, data in max_min_data.items()}
    
    highest_max = max(all_maxes, key=lambda k: all_maxes[k])
    lowest_min = min(all_mins, key=lambda k: all_mins[k])
    
    return {
        "highest_max": {
            "ticker": highest_max,
            "value": all_maxes[highest_max]
        },
        "lowest_min": {
            "ticker": lowest_min,
            "value": all_mins[lowest_min]
        },
        "all_data": max_min_data
    }

# --- Helper to convert frozendict -> dict ---
def to_dict(obj):
    """Converte frozendict in dict per la serializzazione JSON"""
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_dict(i) for i in obj]
    else:
        return obj

# --- Main endpoint ---
@app.post("/prompt")
async def receive_prompt(data: PromptRequest):
    """
    Endpoint principale per l'analisi di dati finanziari tramite linguaggio naturale.
    
    Accetta una richiesta in linguaggio naturale e restituisce:
    - Dati strutturati in formato JSON
    - Analisi in linguaggio naturale
    """
    print(f"Received prompt: {data.prompt}")

    # --- First GPT call: structured JSON with normalized periods ---
    system_prompt = {
        "role": "system",
        "content": (
            "Sei un assistente finanziario che riceve domande in linguaggio naturale. "
            "Devi restituire SOLO un JSON valido senza testo extra. "
            "Struttura JSON: raggruppato per metriche richieste, poi per ticker, poi per periodi/dates. "
            "Includi solo le metriche effettivamente richieste. "
            "Normalizza tutti i periodi in termini che Yahoo Finance può comprendere: "
            "`1mo`, `3mo`, `6mo`, `1y`, `5y`, `ytd` o anni specifici come `2022`, `2025`. "
            "IMPORTANTE: Se non viene specificato esplicitamente un orizzonte temporale, usa `ytd` (Year-to-Date) come periodo predefinito. "
            "Esempio generico:\n"
            "{\n"
            "  \"return\": {\"AAPL\": {\"1y\": null, \"ytd\": null}},\n"
            "  \"compare\": {\"return\": {\"AAPL\": {\"ytd\": null}, \"GOOGL\": {\"ytd\": null}}}\n"
            "}\n"
            "Ticker: simboli ufficiali (Apple=AAPL, Google=GOOGL). "
            "Metriche possibili: return, volatility, fundamentals, max_min, compare. "
            "Non aggiungere testo fuori dal JSON."
        )
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[system_prompt, {"role": "user", "content": data.prompt}],
            temperature=0
        )
        parsed = json.loads(response.choices[0].message.content.strip())
        parsed = to_dict(parsed)  # Convert frozendict -> dict
    except Exception as e:
        return {"status": "error", "message": f"Failed to parse JSON from GPT: {e}"}

    # --- Backend: fill in the values safely ---
    try:
        for metric, tickers_data in parsed.items():
            if metric == "compare":
                for sub_metric, tickers_cmp in tickers_data.items():
                    for ticker, periods in tickers_cmp.items():
                        for period in periods:
                            try:
                                if sub_metric == "return":
                                    tickers_cmp[ticker][period] = to_dict(compare_returns(list(tickers_cmp.keys()), period))
                                elif sub_metric == "volatility":
                                    tickers_cmp[ticker][period] = to_dict(compare_volatility(list(tickers_cmp.keys()), period))
                                elif sub_metric == "fundamentals":
                                    tickers_cmp[ticker][period] = to_dict(compare_fundamentals(list(tickers_cmp.keys())))
                                elif sub_metric == "max_min":
                                    tickers_cmp[ticker][period] = to_dict(compare_max_min(list(tickers_cmp.keys()), period))
                            except Exception:
                                tickers_cmp[ticker][period] = None
            else:
                for ticker, periods in tickers_data.items():
                    # Gestione speciale per fundamentals (non ha periodi)
                    if metric == "fundamentals":
                        try:
                            tickers_data[ticker] = get_fundamentals(ticker)
                        except Exception:
                            tickers_data[ticker] = None
                    else:
                        # Altre metriche con periodi
                        for period in periods:
                            try:
                                if metric == "return":
                                    periods[period] = get_return(ticker, period)
                                elif metric == "volatility":
                                    periods[period] = get_volatility(ticker, period)
                                elif metric == "max_min":
                                    periods[period] = get_max_min(ticker, period)
                            except Exception:
                                periods[period] = None
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch data: {e}"}

    # --- Second GPT call: summarize JSON in natural language ---
    try:
        nl_prompt = f"Analizza questo JSON finanziario e crea una risposta professionale e ben strutturata in italiano. Usa un formato chiaro con paragrafi separati, numerazione quando appropriato, e un linguaggio tecnico ma accessibile. Includi sempre i valori numerici specifici e le percentuali. Struttura la risposta in questo modo: 1) Introduzione breve, 2) Dati principali con valori specifici, 3) Analisi comparativa se presente, 4) Conclusioni. JSON: {json.dumps(parsed)}"
        nl_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": nl_prompt}],
            temperature=0
        )
        nl_text = nl_response.choices[0].message.content.strip()
    except Exception as e:
        nl_text = f"Failed to generate natural language summary: {e}"

    return {
        "status": "ok",
        "result": parsed,
        "natural_language": nl_text
    }

@app.get("/")
async def root():
    """Endpoint di benvenuto con informazioni sull'API"""
    return {
        "message": "Financial Data API",
        "version": "1.0.0",
        "description": "API per l'analisi di dati finanziari con supporto per linguaggio naturale",
        "endpoints": {
            "POST /prompt": "Analisi finanziaria tramite linguaggio naturale",
            "GET /docs": "Documentazione interattiva dell'API"
        }
    }

# --- Run server ---
if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)
