import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime

# ========== 1. 頁面配置 ==========
st.set_page_config(
    page_title="CORA 業務秘書",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ========== 2. 初始化 Gemini API ==========
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
except:
    st.error("❌ API Key 未配置")
    st.stop()

# ========== 3. 本體論數據 - 業務背景 ==========
BUSINESS_CONTEXT = """
我們是一家B2B軟體公司，提供企業決策加速系統。

我們的客戶包括：
- Amazon (年度支出: $2.5M, 風險: Low)
- Google (年度支出: $1.2M, 風險: Medium)
- Tesla (年度支出: $800K, 風險: High)

我們的主要業務政策：
- Low 風險客戶: 最大折扣 15%
- Medium 風險客戶: 最大折扣 5%
- High 風險客戶: 最大折扣 3%

我們的決策框架：
1. 情況分析 (Situation)
2. 策略選項 (Options)
3. AI 建議 (Recommendation)
4. 風險評估 (Risk)
"""

# ========== 4. CSS 樣式優化 ==========
st.markdown("""
<style>
    /* 隱藏底部 Streamlit 標籤 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 最大化內容寬度 */
    .stChatMessage {
        max-width: 100%;
    }
    
    /* 對話框樣式 */
    [data-testid="chatAvatarIcon-assistant"] {
        background-color: #10a37f;
    }
</style>
""", unsafe_allow_html=True)

# ========== 5. 標題 ==========
st.title("🤖 CORA 業務秘書")
st.caption("📊 您的 AI 決策隨側助手 - 提供實時業務建議")
st.divider()

# ========== 6. 對話狀態管理 ==========
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 秘書的開場白
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"""👋 您好！我是 CORA 業務秘書。我來幫助您進行業務決策。

📋 我可以協助您：
• **客戶管理** - 分析客戶信息、商務談判策略
• **銷售決策** - 折扣方案、合同條款建議
• **風險評估** - 交易風險分析、合規檢查
• **策略規劃** - 業務發展建議、市場分析

💡 告訴我您需要什麼幫助，我會基於公司政策和數據給您建議。

例如，您可以問我：
• "Amazon 要求 15% 折扣怎麼辦？"
• "我們應該如何與 Google 續約？"
• "新客戶的信用風險評估"
"""
    })

# ========== 7. 顯示對話歷史 ==========
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ========== 8. 用戶輸入處理 ==========
user_input = st.chat_input("💬 告訴我您需要什麼幫助...")

if user_input:
    # 添加用戶消息到歷史
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 顯示用戶消息
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # 調用 Gemini 生成回覆
    with st.chat_message("assistant"):
        with st.spinner("🤔 思考中..."):
            # 構建系統提示
            system_prompt = f"""你是 CORA 業務秘書。你是一個專業的業務顧問，幫助公司進行決策。

公司背景信息：
{BUSINESS_CONTEXT}

對話歷史：
"""
            
            # 添加最近的對話歷史（最後5條消息）
            recent_messages = st.session_state.messages[-5:]
            for msg in recent_messages[:-1]:  # 排除最新的用戶消息（已在 user_input 中）
                role = "user" if msg["role"] == "user" else "assistant"
                system_prompt += f"\n{role}: {msg['content']}"
            
            system_prompt += f"""

你的角色和指導原則：
1. **專業** - 基於公司政策和數據給建議
2. **清晰** - 用易懂的方式解釋複雜概念
3. **完整** - 提供情況分析、選項、建議、風險評估
4. **可操作** - 給出具體的行動建議
5. **合規** - 確保所有建議符合公司政策

用戶的最新問題：{user_input}

請以友好但專業的語氣回答。使用 emoji 使回答更易讀。如果涉及政策或風險，請明確說明。
"""
            
            try:
                response = model.generate_content(system_prompt)
                assistant_message = response.text
                
                # 添加到歷史
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                # 顯示回覆
                st.markdown(assistant_message)
                
            except Exception as e:
                error_msg = f"❌ 出現問題：{str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# ========== 9. 側邊欄 - 會話管理 ==========
with st.sidebar:
    st.markdown("---")
    
    if st.button("🔄 清空對話"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📌 快速參考")
    st.markdown("""
    **常見問題：**
    - 客戶折扣政策
    - 合同條款建議
    - 風險評估標準
    - 續約策略分析
    """)
    
    st.markdown("---")
    st.markdown("#### 💡 提示")
    st.markdown("自然地描述您的業務場景，我會提供針對性的建議。")
