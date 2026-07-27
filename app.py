import streamlit as st
import pandas as pd
from google import genai
from google.genai.errors import APIError
from monday_service import MondayDataService

st.set_page_config(
    page_title="Skylark BI Agent — Monday.com Assistant",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Monday.com Business Intelligence Agent")
st.caption("Executive BI assistant for Skylark Drones founders & leadership.")

# ------------------------------------------------------------------------------
# Sidebar Credentials & Config
# ------------------------------------------------------------------------------
st.sidebar.header("🔑 Credentials & Config")

monday_api_key = st.sidebar.text_input("Monday API Key", type="password")
gemini_api_key = st.sidebar.text_input("Gemini API Key", type="password")
deals_board_id = st.sidebar.text_input("Deals Board ID", value="5030218428")
work_orders_board_id = st.sidebar.text_input("Work Orders Board ID", value="5030218473")

# Cached data loader to avoid hitting Monday.com rate limits
@st.cache_data(ttl=600, show_spinner=False)
def fetch_monday_boards(m_key: str, d_id: str, wo_id: str):
    service = MondayDataService(m_key)
    deals_df = service.fetch_board_data(d_id)
    wo_df = service.fetch_board_data(wo_id)
    return deals_df, wo_df

if st.sidebar.button("Sync Monday.com Data"):
    if not (monday_api_key.strip() and deals_board_id.strip() and work_orders_board_id.strip()):
        st.sidebar.error("Please provide a valid Monday API Key and Board IDs.")
    else:
        with st.spinner("Fetching dynamic board data from Monday.com..."):
            try:
                deals, work_orders = fetch_monday_boards(
                    monday_api_key.strip(), 
                    deals_board_id.strip(), 
                    work_orders_board_id.strip()
                )
                
                if deals.empty and work_orders.empty:
                    st.sidebar.warning("Synced, but both boards returned empty data.")
                else:
                    st.session_state.deals_df = deals
                    st.session_state.wo_df = work_orders
                    st.sidebar.success(f"Synced! Deals ({len(deals)} rows), Work Orders ({len(work_orders)} rows).")
            except Exception as e:
                st.sidebar.error(f"Failed to fetch data: {str(e)}")

# ------------------------------------------------------------------------------
# Chat History & Interface
# ------------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello Founder! Ask me any question about your deals pipeline, work orders, operational status, or sector performance."
        }
    ]

# Render prior messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Prompt Input
if prompt := st.chat_input("e.g. How is our pipeline looking for the energy sector this quarter?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Validation Checks
    if "deals_df" not in st.session_state or "wo_df" not in st.session_state:
        error_msg = "Please click **'Sync Monday.com Data'** in the sidebar before asking questions!"
        st.error(error_msg)
    elif not gemini_api_key.strip():
        error_msg = "Please provide your **Gemini API Key** in the sidebar."
        st.error(error_msg)
    else:
        clean_gemini_key = gemini_api_key.strip()
        
        with st.chat_message("assistant"):
            with st.spinner("Analyzing pipeline & operational data..."):
                try:
                    client = genai.Client(api_key=clean_gemini_key)
                    
                    # Convert DataFrames to markdown table format for the LLM
                    deals_markdown = st.session_state.deals_df.to_markdown(index=False)
                    wo_markdown = st.session_state.wo_df.to_markdown(index=False)
                    
                    system_prompt = f"""
                    You are an Executive Business Intelligence Agent for Skylark Drones leadership and founders.
                    Your objective is to deliver precise, high-level, data-backed insights across sales pipeline and execution data.

                    ### 1. Deals Board Data (Sales Pipeline):
                    {deals_markdown}

                    ### 2. Work Orders Board Data (Execution & Projects):
                    {wo_markdown}

                    ### User Query:
                    {prompt}

                    ### Response Guidelines:
                    1. **Direct Answer & Metrics:** Start with concise executive summary numbers (Total Revenue, Pipeline Value, Conversion Rates, Project Counts).
                    2. **Cross-Board Analysis:** Combine metrics from both Deals and Work Orders where appropriate.
                    3. **Data Quality Warnings & Caveats:** Highlight missing values, unassigned owners, or unformatted close dates that impact accuracy.
                    4. **Leadership Brief:** Conclude with a clearly labeled "### Leadership Brief" section offering strategic recommendations and risk assessments.
                    """

                    # Query model with fallback handling
                    model_name = "gemini-2.5-flash"
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=system_prompt,
                        )
                        answer = response.text
                    except APIError:
                        # Fallback to gemini-2.0-flash if 2.5 is unavailable in the region
                        response = client.models.generate_content(
                            model="gemini-2.0-flash",
                            contents=system_prompt,
                        )
                        answer = response.text

                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                except APIError as e:
                    err_txt = f"**Gemini API Error:** {e.message}\nPlease verify your API key at [aistudio.google.com](https://aistudio.google.com)."
                    st.error(err_txt)
                except Exception as e:
                    err_txt = f"**Error processing query:** {str(e)}"
                    st.error(err_txt)
