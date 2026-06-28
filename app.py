import streamlit as st
import os
import json
import pandas as pd

# Import local modules
try:
    from detector import detect_bugs
    from ga_engine import evolve_fix
    from validator import validate_fix
    from memory import save_fix, recall_similar_fix
    from report import generate_report
except ImportError as e:
    st.error(f"Failed to import local modules: {e}")

# Page config
st.set_page_config(
    page_title="Code Review Agent",
    page_icon="🤖",
    layout="wide"
)

# Hardcoded sample buggy codes
BUG_1_CODE = """def divide_numbers(a, b):
    # This function has a potential division by zero bug
    result = a / b
    return result
"""

BUG_2_CODE = """def read_log_file(filename):
    # This function opens a file but does not close it
    f = open(filename, 'r')
    content = f.read()
    return content
"""

BUG_3_CODE = """def factorial(n):
    # This function will cause infinite recursion
    return n * factorial(n - 1)
"""

# Initialize session state variables
if "code" not in st.session_state:
    st.session_state["code"] = ""
if "bugs" not in st.session_state:
    st.session_state["bugs"] = []
if "fixes" not in st.session_state:
    st.session_state["fixes"] = []
if "code_input" not in st.session_state:
    st.session_state["code_input"] = ""

# --- SIDEBAR SECTION ---
st.sidebar.title("Settings & Config")

# API key input
api_key_input = st.sidebar.text_input("Groq API Key", type="password", value=st.session_state.get("api_key", ""))
if api_key_input:
    st.session_state["api_key"] = api_key_input
    st.sidebar.success("✅ API Key Set")
else:
    st.session_state["api_key"] = ""

# GA hyperparameters sliders
generations = st.sidebar.slider("Generations", min_value=3, max_value=5, value=3)
st.session_state["generations"] = generations

pop_size = st.sidebar.slider("Population Size", min_value=4, max_value=6, value=4)
st.session_state["pop_size"] = pop_size


# --- HEADER SECTION ---
st.title("🤖 Autonomous Code Review & Bug Fix Agent")
st.caption("Powered by Groq Llama-3.1 + Genetic Algorithms")


# --- TABS CREATION ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Code Input",
    "🐛 Bug Detection",
    "🧬 Fix Evolution (GA)",
    "📄 Results & Report"
])


# --- TAB 1: Code Input ---
with tab1:
    st.subheader("Input Python Code")

    # Sample code loading buttons
    st.write("Load a sample buggy code snippet:")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Load Bug 1: Division by Zero"):
            st.session_state["code_input"] = BUG_1_CODE
            st.rerun()
    with col2:
        if st.button("Load Bug 2: File Not Closed"):
            st.session_state["code_input"] = BUG_2_CODE
            st.rerun()
    with col3:
        if st.button("Load Bug 3: Infinite Recursion"):
            st.session_state["code_input"] = BUG_3_CODE
            st.rerun()

    # Text area for code editing
    code_text = st.text_area("Edit or type your Python code below:", value=st.session_state["code_input"], height=300)

    # Start analysis action
    if st.button("🔍 Start Analysis"):
        api_key = st.session_state.get("api_key")
        if not api_key:
            st.warning("Please enter your Groq API Key in the sidebar first.")
        elif not code_text.strip():
            st.warning("Please enter some Python code before starting analysis.")
        else:
            try:
                with st.spinner("Analyzing code for bugs..."):
                    detected_bugs = detect_bugs(code_text, api_key)
                
                st.session_state["bugs"] = detected_bugs
                st.session_state["code"] = code_text
                # Reset previous fixes when new analysis starts
                st.session_state["fixes"] = []
                
                st.success(f"Analysis completed. Found {len(detected_bugs)} bug(s)!")
            except Exception as e:
                st.error(f"Error during bug detection module execution: {e}")


# --- TAB 2: Bug Detection ---
with tab2:
    bugs = st.session_state.get("bugs", [])
    if not bugs:
        st.info("No bugs detected yet. Go to 'Code Input' tab to run an analysis.")
    else:
        st.subheader("Detected Bug Analysis")

        # Metric total
        st.metric("Total Bugs Found", len(bugs))

        # Severity chart
        try:
            counts = {"high": 0, "medium": 0, "low": 0}
            for bug in bugs:
                sev = bug.get("severity", "").lower()
                if sev in counts:
                    counts[sev] += 1
            
            chart_df = pd.DataFrame(
                list(counts.items()),
                columns=["Severity", "Count"]
            ).set_index("Severity")
            
            st.bar_chart(chart_df)
        except Exception as chart_err:
            st.error(f"Error building severity chart: {chart_err}")

        # Bug Table Dataframe
        try:
            emoji_map = {
                "high": "🔴 High",
                "medium": "🟡 Medium",
                "low": "🟢 Low"
            }
            formatted_bugs = []
            for bug in bugs:
                formatted_bugs.append({
                    "Line": bug.get("line_number"),
                    "Type": bug.get("bug_type"),
                    "Severity": emoji_map.get(bug.get("severity", "").lower(), bug.get("severity")),
                    "Description": bug.get("description")
                })
            
            st.dataframe(pd.DataFrame(formatted_bugs), use_container_width=True)
        except Exception as df_err:
            st.error(f"Error rendering bug dataframe: {df_err}")


# --- TAB 3: Fix Evolution (GA) ---
with tab3:
    bugs = st.session_state.get("bugs", [])
    code = st.session_state.get("code", "")
    api_key = st.session_state.get("api_key", "")

    if not bugs:
        st.info("No bugs detected yet. Go to 'Code Input' tab to run an analysis.")
    else:
        st.subheader("Genetic Algorithm Fix Evolution")
        
        # Trigger evolution process
        if st.button("🚀 Evolve Fixes"):
            if not api_key:
                st.warning("Please enter your Groq API Key in the sidebar.")
            else:
                fixes = []
                for idx, bug in enumerate(bugs):
                    st.write("---")
                    st.markdown(f"### Bug {idx + 1}: {bug.get('description')}")
                    
                    # 1. Memory Check
                    try:
                        recalled_fix = recall_similar_fix(bug.get("description"))
                    except Exception as mem_err:
                        st.error(f"Error calling recall_similar_fix: {mem_err}")
                        recalled_fix = None

                    if recalled_fix:
                        st.info("Memory hit! Similar bug fix retrieved from memory.")
                        fix = recalled_fix
                        st.progress(1.0)
                    else:
                        st.write("No matching fix in memory. Running evolution algorithm...")
                        # 2. Run Evolution
                        try:
                            with st.spinner("Running Genetic Algorithm..."):
                                fix = evolve_fix(code, bug, api_key)
                            st.progress(1.0)
                        except Exception as ga_err:
                            st.error(f"Error running evolve_fix: {ga_err}")
                            fix = code  # Fallback to original

                        # 3. Save to Memory
                        try:
                            save_fix(bug.get("description"), fix)
                        except Exception as save_err:
                            st.error(f"Error saving fix to memory: {save_err}")

                    # 4. Validate Fix
                    try:
                        v_res = validate_fix(code, fix)
                        st.metric("Validation Score", v_res.get("score"))
                        st.write(f"**Syntax is Valid:** {v_res.get('is_valid')} | **Lines Changed:** {v_res.get('lines_changed')}")
                    except Exception as val_err:
                        st.error(f"Error validating fix: {val_err}")
                        v_res = {"diff": "", "is_valid": False}

                    # Show side-by-side code Comparison
                    col_orig, col_fixed = st.columns(2)
                    with col_orig:
                        st.markdown("**Original Code:**")
                        st.code(code, language="python")
                    with col_fixed:
                        st.markdown("**Fixed Code:**")
                        st.code(fix, language="python")

                    # Show unified diff
                    st.markdown("**Unified Diff:**")
                    st.code(v_res.get("diff"), language="diff")
                    
                    fixes.append(fix)
                st.session_state["fixes"] = fixes
        
        # Display existing evolved fixes if already generated
        elif st.session_state.get("fixes"):
            for idx, bug in enumerate(bugs):
                if idx < len(st.session_state["fixes"]):
                    st.write("---")
                    st.markdown(f"### Bug {idx + 1}: {bug.get('description')}")
                    fix = st.session_state["fixes"][idx]

                    try:
                        v_res = validate_fix(code, fix)
                        st.metric("Validation Score", v_res.get("score"))
                        st.write(f"**Syntax is Valid:** {v_res.get('is_valid')} | **Lines Changed:** {v_res.get('lines_changed')}")
                    except Exception as val_err:
                        st.error(f"Error validating fix: {val_err}")
                        v_res = {"diff": "", "is_valid": False}

                    col_orig, col_fixed = st.columns(2)
                    with col_orig:
                        st.markdown("**Original/Before:**")
                        st.code(code, language="python")
                    with col_fixed:
                        st.markdown("**Fixed/Evolved:**")
                        st.code(fix, language="python")

                    st.markdown("**Unified Diff:**")
                    st.code(v_res.get("diff"), language="diff")


# --- TAB 4: Results & Report ---
with tab4:
    fixes = st.session_state.get("fixes", [])
    bugs = st.session_state.get("bugs", [])
    code = st.session_state.get("code", "")

    if not fixes:
        st.info("No fixes generated yet. Go to 'Fix Evolution (GA)' tab to evolve solutions.")
    else:
        st.subheader("Code Review Summary Report")

        # Recommendation alert style
        try:
            severities = [bug.get("severity", "").lower() for bug in bugs]
            if "high" in severities:
                st.error("🔴 Recommendation: CRITICAL. High severity bugs remain unresolved in the codebase. Immediate review required.")
            elif "medium" in severities:
                st.warning("🟡 Recommendation: NEEDS FIX. Medium severity bugs require addressment.")
            else:
                st.success("🟢 Recommendation: PASS. Code reviews check out clean with minimal low-risk bugs.")
        except Exception as rec_err:
            st.error(f"Error calculating recommendation: {rec_err}")

        # Render report markdown
        try:
            md_report = generate_report(code, bugs, fixes)
            st.markdown(md_report)
        except Exception as rep_err:
            st.error(f"Error generating report: {rep_err}")

        # PDF download button
        pdf_path = "code_review_report.pdf"
        if os.path.exists(pdf_path):
            try:
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name="code_review_report.pdf",
                    mime="application/pdf"
                )
            except Exception as pdf_read_err:
                st.error(f"Error reading PDF report file: {pdf_read_err}")
