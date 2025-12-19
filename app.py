import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json

# --- 1. 頁面配置 ---
st.set_page_config(page_title="CORA 5.0 Leaf Secretary", layout="wide")

# --- 2. 初始化 ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
except:
    st.error("❌ API Key 未配置")
    st.stop()

# 本體論數據
customers = {
    "Amazon": {
        "industry": "E-Commerce",
        "spend": "$2.5M", 
        "risk": "Low", 
        "history": "長期合作夥伴，過去3年每年增長10%。最近在詢問新產品線。",
        "pain_points": "希望降低運維成本，對價格敏感度中等。",
        "limit": 15
    },
    "Google": {
        "industry": "Tech",
        "spend": "$1.2M", 
        "risk": "Medium", 
        "history": "合同還有3個月到期，競爭對手正在接觸他們。",
        "pain_points": "需要更高的SLA服務等級，對價格不敏感，但對質量要求極高。",
        "limit": 5
    },
    "Tesla": {
        "industry": "Automotive",
        "spend": "$800K", 
        "risk": "High", 
        "history": "去年有兩次延遲付款記錄。正在進行工廠數字化轉型。",
        "pain_points": "預算被削減，需要極致的性價比。",
        "limit": 3
    }
}

# --- 3. 側邊欄 ---
st.sidebar.title("⚙️ CORA 控制台")
selected_customer = st.sidebar.selectbox("選擇客戶", list(customers.keys()))
customer = customers[selected_customer]

# 顯示客戶信息卡
with st.sidebar:
    st.markdown(f"""
    ### 📊 {selected_customer}
    - **支出**: {customer['spend']}
    - **風險**: {customer['risk']}
    - **行業**: {customer['industry']}
    - **折扣限額**: {customer['limit']}%
    """)

# --- 4. 主要區域 - 兩欄佈局 ---
col_chat, col_spine = st.columns([2.5, 1])

# === 左欄：Leaf 對話介面 ===
with col_chat:
    st.title("🍃 Leaf - 你的 AI 決策秘書")
    st.caption(f"正在協助：{selected_customer} 續約談判")
    
    # 初始化對話歷史 (Session State)
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # 秘書的開場白
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"👋 你好！我是 CORA Leaf 決策秘書。我已經準備好幫你分析 {selected_customer} 的續約策略。\n\n💡 你可以問我：\n- '為 {selected_customer} 生成談判簡報'\n- '如果給 12% 折扣會怎樣？'\n- '有什麼風險我應該知道？'"
        })
    
    # 顯示對話歷史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 用戶輸入框
    user_input = st.chat_input(f"詢問關於 {selected_customer} 的任何事項...")
    
    if user_input:
        # 添加用戶消息到歷史
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # 顯示用戶消息
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # 調用 Gemini 生成回覆
        with st.chat_message("assistant"):
            with st.spinner("🤔 思考中..."):
                # 構建上下文
                prompt = f"""
                你是 CORA 系統的 Leaf 智能決策秘書。你已經掌握了企業客戶的信息。
                
                目前客戶：{selected_customer}
                客戶背景：
                - 行業：{customer['industry']}
                - 年度支出：{customer['spend']}
                - 風險等級：{customer['risk']}
                - 歷史記錄：{customer['history']}
                - 痛點：{customer['pain_points']}
                - 系統允許的最大折扣：{customer['limit']}%
                
                用戶的問題：{user_input}
                
                請以專業但友好的語氣，像一個資深顧問一樣回答。
                - 如果涉及折扣決策，提醒系統的限制是 {customer['limit']}%
                - 如果用戶詢問風險，要基於客戶的 {customer['risk']} 風險等級
                - 使用 emoji 和簡潔的格式讓內容易讀
                - 回答要控制在 150 字以內
                """
                
                try:
                    response = model.generate_content(prompt)
                    assistant_message = response.text
                    
                    # 添加到歷史
                    st.session_state.messages.append({"role": "assistant", "content": assistant_message})
                    
                    # 顯示回覆
                    st.markdown(assistant_message)
                    
                except Exception as e:
                    st.error(f"❌ AI 生成失敗: {e}")
                    error_msg = f"抱歉，我遇到了一個技術問題。錯誤：{str(e)}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    st.markdown(error_msg)

# === 右欄：Spine 治理 ===
with col_spine:
    st.title("🛡️ Spine")
    st.caption("治理引擎")
    
    st.divider()
    
    with st.container(border=True):
        st.markdown(f"**風險等級**: {customer['risk']}")
        st.markdown(f"**折扣限額**: {customer['limit']}%")
        
        discount_input = st.number_input(
            "您的折扣決策 (%)",
            0, 100, customer['limit'], 
            key=f"discount_{selected_customer}"
        )
        
        if st.button("✅ 提交決策", use_container_width=True):
            with st.spinner("正在檢查..."):
                if discount_input > customer['limit']:
                    st.error(f"❌ 違規！最大 {customer['limit']}%")
                    st.warning(f"您輸入：{discount_input}%")
                    st.info("🚨 已自動上報財務總監")
                else:
                    st.success(f"✅ 批准！{discount_input}% 折扣符合規則")
                    st.info("📝 合同草稿已發送給法務部門")
