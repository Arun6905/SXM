import streamlit as st
import asyncio
import pandas as pd
from multi_agent_system import PlannerAgent

# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------
st.set_page_config(
    page_title="Agentic Bug Hunter",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# CUSTOM CSS FOR DARK THEME & STYLING
# ---------------------------------------------------
st.markdown("""
<style>
    /* Main Background & Text Color */
    .stApp {
        background-color: #FFFFFF;
        color: #C9D1D9;
        font-family: 'Inter', sans-serif;
    }
    
    /* Headings */
    h1, h2, h3, h4 {
        color: #000000 !important;
        font-weight: 600 !important;
    }

    /* Buttons */
    div.stButton > button {
        background-color: #238636 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        background-color: #2EA043 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(46, 160, 67, 0.4);
    }
    
    div.stDownloadButton > button {
        background-color: #1F6FEB !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    div.stDownloadButton > button:hover {
        background-color: #388BFD !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(56, 139, 253, 0.4);
    }

    /* Inputs, Selectboxes, Textareas, File Uploader */
    .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        color: #C9D1D9 !important;
        border-radius: 8px !important;
    }
    
    /* File Uploader override */
    div[data-testid="stFileUploader"] {
        background-color: #161B22 !important;
        border: 1px dashed #30363D !important;
        border-radius: 8px !important;
        padding: 10px;
    }

    /* Alert cards (st.info, st.error, st.success) */
    div[data-testid="stAlert"] {
        border-radius: 8px !important;
        border-left-width: 5px !important;
    }

    /* Horizontal line dividers */
    hr {
        border-color: #30363D !important;
        opacity: 0.5 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HEADER SECTION
# ---------------------------------------------------
st.title("🤖 Agentic Bug Hunter")
st.markdown("#### **Multi-Agent + MCP Debugging System**")
st.markdown("Upload or paste your code below and let our intelligent agents find and fix the bugs.")
st.markdown("---")

planner = PlannerAgent()

# ---------------------------------------------------
# INPUT SECTION (DASHBOARD LAYOUT)
# ---------------------------------------------------
with st.container():
    st.markdown("### 📂 Configuration & Code Input")
    col_input1, col_input2 = st.columns([1, 2])
    
    with col_input1:
        language = st.selectbox(
            "💻 Select Programming Language:",
            ["Python", "C++"]
        )
        
        if language == "Python":
            file_types = ["py"]
        else:
            file_types = ["cpp", "cc", "cxx", "h"]
            
        uploaded_file = st.file_uploader(
            f"Upload {language} file",
            type=file_types
        )
        
    with col_input2:
        code_input = st.text_area(
            f"📝 Or paste your {language} code here:",
            height=200,
            placeholder=f"// Enter {language} code to analyze..."
        )

final_code = ""

if uploaded_file is not None:
    final_code = uploaded_file.read().decode("utf-8", errors="ignore")
elif code_input.strip():
    final_code = code_input

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------
# ANALYZE BUTTON
# ---------------------------------------------------
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

with col_btn2:
    analyze_clicked = st.button("🚀 Analyze Code")

if analyze_clicked:
    if not final_code.strip():
        st.warning("⚠️ Please upload or paste code before analyzing.")
        st.stop()

    with st.spinner(f"🔍 Analyzing {language} code via Multi-Agent + MCP... please wait."):
        # Custom async handler to prevent 'Event loop is closed' errors in Streamlit
        def run_async(coro):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)

        result = run_async(planner.handle_request(final_code, language))

    st.markdown("---")

    # ---------------------------------------------------
    # NO BUG CASE
    # ---------------------------------------------------
    if not result["bug_found"]:
        st.success("✅ **Great news!** No bugs detected in your code.")
        st.balloons()
        st.stop()

    # ---------------------------------------------------
    # BUG DISPLAY & FIX SECTION
    # ---------------------------------------------------
    st.markdown("## 🐞 Bug Detection Report")
    
    with st.container():
        col_bug, col_fix = st.columns(2)

        with col_bug:
            st.error("#### ❌ Bug Detected")
            st.markdown(f"**Line Number:** `{result['bug_line']}`")
            st.markdown(f"**Error Type:** `{result['error_type']}`")
            st.markdown("**Explanation:**")
            st.info(result['explanation'])

        with col_fix:
            st.success("#### 💡 corrected_code")
            if language == "Python":
                st.code(result["corrected_code"], language="python")
            else:
                st.code(result["corrected_code"], language="cpp")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------
    # VERIFICATION & EXPORT SECTION
    # ---------------------------------------------------
    col_ver, col_out = st.columns(2)
    
    with col_ver:
        with st.container():
            st.markdown("### 🤖 Agent Verification")
            if result["verification"]["verification_passed"]:
                st.success("##### ✅ Verification Passed")
                st.markdown("The suggested fix has been verified successfully by the agent.")
            else:
                st.error("##### ❌ Verification Failed")
                st.markdown(f"**Reason:** {result['verification']['verification_message']}")

    with col_out:
        with st.container():
            st.markdown("### 📄 Output Export")
            st.markdown("Submission format for the detected bug:")
            
            df = pd.DataFrame([
                {
                    "ID": 0,
                    "Bug Line": result["bug_line"],
                    "Explanation": result["explanation"]
                }
            ], columns=["ID", "Bug Line", "Explanation"])

            st.dataframe(df, use_container_width=True)

            csv_data = df.to_csv(index=False).encode("utf-8")

            col_down_btn1, col_down_btn2 = st.columns([1, 1])
            with col_down_btn1:
                st.download_button(
                    label="⬇️ Download output.csv",
                    data=csv_data,
                    file_name="output.csv",
                    mime="text/csv"
                )
