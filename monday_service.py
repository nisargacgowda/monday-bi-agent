import requests
import pandas as pd

MONDAY_API_URL = "https://api.monday.com/v2"

class MondayDataService:
    def __init__(self, api_key: str):
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
            "API-Version": "2023-10"
        }

    def fetch_board_data(self, board_id: str) -> pd.DataFrame:
        """Fetch all items and column values from a Monday.com board."""
        query = f"""
        query {{
          boards(ids: {board_id}) {{
            items_page (limit: 500) {{
              items {{
                id
                name
                column_values {{
                  column {{
                    title
                  }}
                  text
                }}
              }}
            }}
          }}
        }}
        """
        response = requests.post(MONDAY_API_URL, json={'query': query}, headers=self.headers)
        data = response.json()
        
        try:
            items = data['data']['boards'][0]['items_page']['items']
        except (KeyError, IndexError, TypeError):
            return pd.DataFrame()

        rows = []
        for item in items:
            row = {'Item Name': item['name']}
            for col in item['column_values']:
                col_title = col['column']['title'] if col.get('column') else 'Unknown'
                row[col_title] = col.get('text', '')
            rows.append(row)
            
        df = pd.DataFrame(rows)
        return self._clean_data(df)

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing data and dirty formats gracefully."""
        if df.empty:
            return df
            
        # Fill missing text values
        df = df.fillna("Unassigned / Missing")
        
        # Clean currency & numerical columns automatically
        for col in df.columns:
            if any(word in col.lower() for word in ['value', 'amount', 'revenue', 'cost', 'price']):
                df[col] = df[col].astype(str).str.replace(r'[\$,]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
        return df
