# Monday.com Business Intelligence Agent — Skylark Drones

An AI-powered Business Intelligence agent that integrates dynamically with Monday.com boards (Deals & Work Orders) to answer executive queries, analyze sector performance, and generate leadership briefs.

## 🏗️ Architecture Overview
- **UI & Interface:** Streamlit (Hosted on Streamlit Community Cloud)
- **Data Integration:** Monday.com GraphQL API (`api.monday.com/v2`)
- **Data Processing:** Pandas (in-memory cleaning, currency stripping, null handling)
- **Intelligence Engine:** Google GenAI SDK (`gemini-3.6-flash`)

## 📁 Repository Structure
- `app.py`: Main Streamlit conversational UI and LLM integration.
- `monday_service.py`: Dynamic GraphQL client and data normalization layer.
- `requirements.txt`: Python package dependencies.
- `README.md`: Setup and technical documentation.

## 🛠️ Setup & Configuration Instructions
1. Clone this repository to your local machine.
2. Install the required Python package dependencies:
   ```bash
   pip install -r requirements.txt

1.Import the CSV datasets into Monday.com as two separate boards: Deals and Work Orders.
2.Obtain your Monday API Token, Deals Board ID, and Work Orders Board ID from your Monday.com workspace.
3.Generate a Gemini API Key from Google AI Studio.
4.Run the application locally:
   Bash
   streamlit run app.py
5.Enter your credentials in the Streamlit sidebar and click Sync Monday.com Data.
