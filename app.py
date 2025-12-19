import streamlit as st
import google.generativeai as genai
import time

st.set_page_config(page_title="CORA 5.0 (Gemini Powered)", layout="wide")

st.title("🚀 CORA 5.0 Enterprise Decision System")
st.caption("Powered by Google Gemini Pro")

st.sidebar.header("⚙️ Control Panel")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    api_status = "✅ AI Connection Successful"
except:
    api_status = "❌ API Key Not Detected"
    st.error("Please configure GEMINI_API_KEY in Streamlit Secrets")

st.sidebar.text(api_status)

customers = {
    "Amazon": {
        "industry": "E-Commerce",
        "spend": "$2.5M",
        "risk": "Low",
        "history": "Long-term partner, 10% annual growth for 3 years.",
        "pain_points": "Wants to reduce operational costs."
    },
    "Google": {
        "industry": "Tech",
        "spend": "$1.2M",
        "risk": "Medium",
        "history": "Contract expires in 3 months. Competitors reaching out.",
        "pain_points": "Needs higher SLA levels. Quality critical."
    },
    "Tesla": {
        "industry": "Automotive",
        "spend": "$800K",
        "risk": "High",
        "history": "Two late payment records last year.",
        "pain_points": "Budget cuts. Needs cost-effectiveness."
    }
}

selected_customer_name = st.sidebar.selectbox("Select Target Customer", list(customers.keys()))
customer_data = customers[selected_customer_name]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Customer Name", selected_customer_name)
col2.metric("Annual Spend", customer_data['spend'])
col3.metric("Risk Score", customer_data['risk'])
col4.metric("Industry", customer_data['industry'])

st.divider()

st.subheader("🍃 Leaf: Intelligent Decision Brief Generation")
st.info(f"Current Task: Prepare strategy for {selected_customer_name} renewal negotiation")

if st.button("✨ Call AI to Generate Real-Time Brief"):
    if api_status.startswith("❌"):
        st.error("Cannot generate: Please configure API Key first")
    else:
        with st.spinner('Orchestrating intelligent agents: Analyzing data...'):
            prompt = f"""
            You are the 'Leaf' agent in the CORA system. Generate a sales decision brief.
            
            Customer Data:
            - Name: {selected_customer_name}
            - Industry: {customer_data['industry']}
            - Background: {customer_data['history']}
            - Pain Points: {customer_data['pain_points']}
            - Risk Level: {customer_data['risk']}
            
            Generate a Markdown brief with:
            1. **Situation Analysis**: Professional analysis
            2. **Strategy Options**: 3 specific options (conservative, balanced, aggressive)
            3. **CORA Recommendation**: Final recommendation
            """
            
            try:
                response = model.generate_content(prompt)
                st.success("Generation Complete!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"AI generation failed: {e}")

st.divider()

st.subheader("🛡️ Spine: Risk Governance & Compliance")
st.caption("Try entering a discount. If it exceeds the limit, it will be blocked.")

limit = 15 if customer_data['risk'] == "Low" else 5
st.write(f"Current customer risk is **{customer_data['risk']}**, system auto-set max discount to **{limit}%**")

discount = st.number_input("Enter Proposed Discount (%)", 0, 100, 10)

if st.button("Submit Decision"):
    with st.spinner('Spine evaluating compliance rules...'):
        time.sleep(0.5)
    
    if discount > limit:
        st.error(f"❌ Blocked! Spine detected violation")
        st.warning(f"Reason: Max discount for {selected_customer_name} is {limit}%, you entered {discount}%.")
        st.markdown("**Execution Action**: \n* 🚫 Auto-reject request\n* 📩 Send alert report to regional director")
    else:
        st.success("✅ Approved! Decision complies with governance rules")
        st.markdown("**Execution Action**: \n* 📝 Auto-generate contract draft\n* 📧 Notify legal department")
