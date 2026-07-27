import streamlit as st
import pandas as pd
from openai import OpenAI
from monday_service import MondayDataService

st.set_page_config(page_title="Skylark BI Agent", layout="wide")
st.title("📊 Monday.com Business Intelligence Agent")

# Sidebar Credentials
st.sidebar.header("🔑 Credentials & Config")
monday_api_key = st.sidebar.text_input("Monday API Key", type="password")
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
deals_board_id = st.sidebar.text_input("Deals Board ID")
work_orders_board_id = st.sidebar.text_input("Work Orders Board ID")

@st.cache_data(ttl=600)
def load_data(api_key, deals_id, wo_id):
    service = MondayDataService(api_key)
    deals_df = service.fetch_board_data(deals_id)
    wo_df = service.fetch_board_data(wo_id)
    return deals_df, wo_df

if st.sidebar.button("Sync Monday.com Data"):
    if not (monday_api_key and deals_board_id and work_orders_board_id):
        st.error("Please fill in Monday API Key and Board IDs in the sidebar.")
    else:
        with st.spinner("Fetching board data dynamically from Monday.com..."):
            deals_df, wo_df = load_data(monday_api_key, deals_board_id, work_orders_board_id)
            st.session_state.deals_df = deals_df
            st.session_state.wo_df = wo_df
            st.sidebar.success("Successfully synced data!")

# Conversational Interface
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello Founder! Ask me any question about your deals pipeline, work orders, or sector performance."}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("e.g. How is our pipeline looking for energy sector this quarter?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if "deals_df" not in st.session_state or "wo_df" not in st.session_state:
        st.error("Please click 'Sync Monday.com Data' in the sidebar first!")
    elif not openai_api_key:
        st.error("Please provide an OpenAI API key in the sidebar.")
    else:
        client = OpenAI(api_key=openai_api_key)
        
        deals_summary = st.session_state.deals_df.to_markdown(index=False)
        wo_summary = st.session_state.wo_df.to_markdown(index=False)
        
        system_prompt = f"""
        You are an executive BI Assistant for Skylark Drones founders.
        Analyze the provided Monday.com board data to answer executive business queries.
        
        ### Deals Board Data:
        {deals_summary}
        
        ### Work Orders Board Data:
        {wo_summary}
        
        ### Guidance:
        1. Give direct executive summary stats (Revenue, Pipeline value, counts).
        2. Always note **Data Quality Warnings** (e.g., missing close dates, unknown sectors).
        3. Provide actionable insights, not just raw counts.
        4. Include a section titled "Leadership Brief" formatted for executive updates.
        """
        
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = response.choices[0].message.content
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
