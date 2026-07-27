# Monday.com Business Intelligence Agent — Skylark Drones

An AI-powered Business Intelligence agent that integrates dynamically with Monday.com boards (Deals & Work Orders) to answer executive queries, analyze sector performance, and generate leadership briefs.

## 🏗️ Architecture Overview
- **UI & Interface:** Streamlit (Hosted on Streamlit Community Cloud)
- **Data Integration:** Monday.com GraphQL API (`api.monday.com/v2`)
- **Data Processing:** Pandas (in-memory cleaning, currency stripping, null handling)
- **Intelligence Engine:** Google GenAI SDK (`gemini-2.5-flash`)

## 📁 Repository Structure
- `app.py`: Main Streamlit conversational UI and LLM integration.
- `monday_service.py`: Dynamic GraphQL client and data normalization layer.
- `requirements.txt`: Python package dependencies.

## 🛠️ Setup & Configuration Instructions
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
