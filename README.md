# 📊 Financial Data API

A modern REST API for financial data analysis that uses artificial intelligence to interpret natural language queries and provide detailed market analysis.

## 🚀 Key Features

- **Natural Language**: Ask questions about financial markets using natural language
- **Comprehensive Analysis**: Support for returns, volatility, fundamentals, and comparisons
- **Real-time Data**: Integration with Yahoo Finance for up-to-date data
- **REST API**: Modern and well-documented interface
- **CORS Enabled**: Ready for frontend web integration
- **Structured Responses**: JSON data + natural language analysis

## 📈 Supported Metrics

### Single Data Points
- **Returns**: Percentage return calculation for any period
- **Volatility**: Annualized volatility for risk assessment
- **Fundamentals**: Market Cap, P/E Ratio, EPS, Dividend Yield, Debt-to-Equity
- **Highs/Lows**: Extreme prices for specific periods

### Comparisons
- **Return Comparison**: Identify the best performer
- **Volatility Comparison**: Find the most/least risky asset
- **Fundamentals Comparison**: Complete comparative analysis
- **Highs/Lows Comparison**: Identify absolute extremes

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- OpenAI API Key

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/financial-data-api.git
cd financial-data-api
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your OpenAI API Key
```

5. **Start the server**
```bash
python main.py
```

The server will be available at `http://localhost:8000`

## 📚 Usage

### Main Endpoint

**POST** `/prompt`

Send a natural language request to get financial analysis.

#### Example Request
```json
{
  "prompt": "What is Apple's return over the last 3 months?"
}
```

#### Example Response
```json
{
  "status": "ok",
  "result": {
    "return": {
      "AAPL": {
        "3mo": 12.5
      }
    }
  },
  "natural_language": "Apple (AAPL) recorded a return of 12.5% over the last 3 months..."
}
```

### Supported Query Examples

#### Single Data Points
- "What is Tesla's return over the last year?"
- "Show me NVIDIA's volatility over the last 6 months"
- "What are Microsoft's fundamentals?"
- "What is Amazon's high and low over the last 5 years?"

#### Comparisons
- "Which stock performed better between Apple, Google, and Meta?"
- "Compare Tesla and Ford's volatility"
- "Which company has better fundamentals between Apple and Microsoft?"
- "Compare NVIDIA and AMD's highs and lows over the last year"

### Supported Time Periods
- `1mo` - 1 month
- `3mo` - 3 months  
- `6mo` - 6 months
- `1y` - 1 year
- `5y` - 5 years
- `ytd` - Year-to-Date (default if not specified)
- Specific years: `2022`, `2023`, `2024`, etc.

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Configuration
ALLOWED_ORIGINS=*
```

### CORS for Production

For production use, modify `ALLOWED_ORIGINS` to specify allowed domains:

```env
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

## 📖 API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🚀 Deployment

### With ngrok (for testing)
```bash
# In one terminal
python main.py

# In another terminal
ngrok http 8000
```

### With Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### On Cloud Platforms
- **Heroku**: Ready for deployment with Procfile
- **Railway**: Automatically supports Python
- **DigitalOcean App Platform**: Simple configuration
- **AWS/GCP/Azure**: Use containers or serverless

## 🧪 Testing

### Manual Testing
```bash
# Test the main endpoint
curl -X POST "http://localhost:8000/prompt" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is Apple'\''s return over the last 3 months?"}'
```

### Frontend Testing
The API is configured with CORS to allow requests from web frontends.

## 📊 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI        │    │   Yahoo Finance │
│   (React/Vue)   │◄──►│   Server         │◄──►│   API           │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   OpenAI GPT     │
                       │   (NLP Analysis) │
                       └──────────────────┘
```
