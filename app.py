import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ========== 1. 頁面配置 ==========
st.set_page_config(
    page_title="CORA 業務秘書 - 完整版",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ========== 2. 初始化 Gemini API ==========
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
except:
    st.error("❌ API Key 未配置")
    st.stop()

# ========== 3. 初始化 Session State ==========
if "customers" not in st.session_state:
    st.session_state.customers = {}  # {name: {email, company, notes, ...}}
    
if "products" not in st.session_state:
    st.session_state.products = {}  # {name: {price, description, ...}}
    
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "emails_sent" not in st.session_state:
    st.session_state.emails_sent = []  # 記錄已發送的電郵

# ========== 4. 業務背景設定 ==========
COMPANY_INFO = """
我們是一家創新型B2B軟體公司，專注於企業決策加速解決方案。

公司專長：
- 決策流程自動化
- 實時數據分析
- AI驅動的業務洞察

我們歡迎與新客戶建立合作關係。
"""

# ========== 5. CSS 樣式 ==========
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stChatMessage {max-width: 100%;}
</style>
""", unsafe_allow_html=True)

# ========== 6. 主標題 ==========
st.title("🤖 CORA 業務秘書 - 完整版")
st.caption("📊 客戶管理 • 產品推廣 • 電郵聯絡 - 一站式業務AI助手")
st.divider()

# ========== 7. 側邊欄 - 業務數據管理 ==========
with st.sidebar:
    st.markdown("### 📋 業務數據管理")
    
    # 客戶管理
    st.markdown("#### 👥 客戶管理")
    
    with st.expander("➕ 新增客戶", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            cust_name = st.text_input("客戶名稱")
        with col2:
            cust_email = st.text_input("電郵")
        
        cust_company = st.text_input("公司名稱")
        cust_notes = st.text_area("備註 (行業、需求等)")
        
        if st.button("✅ 保存客戶"):
            if cust_name and cust_email:
                st.session_state.customers[cust_name] = {
                    "email": cust_email,
                    "company": cust_company,
                    "notes": cust_notes,
                    "created": datetime.now().isoformat()
                }
                st.success(f"✅ {cust_name} 已添加")
            else:
                st.error("❌ 請填入名稱和電郵")
    
    # 顯示已有客戶
    if st.session_state.customers:
        st.markdown("**已有客戶：**")
        for name in st.session_state.customers.keys():
            st.caption(f"• {name}")
    else:
        st.info("暫無客戶")
    
    st.markdown("---")
    
    # 產品管理
    st.markdown("#### 📦 產品管理")
    
    with st.expander("➕ 新增產品", expanded=False):
        prod_name = st.text_input("產品名稱")
        prod_price = st.text_input("價格")
        prod_desc = st.text_area("產品描述")
        
        if st.button("✅ 保存產品"):
            if prod_name:
                st.session_state.products[prod_name] = {
                    "price": prod_price,
                    "description": prod_desc,
                    "created": datetime.now().isoformat()
                }
                st.success(f"✅ {prod_name} 已添加")
            else:
                st.error("❌ 請填入產品名稱")
    
    # 顯示已有產品
    if st.session_state.products:
        st.markdown("**已有產品：**")
        for name in st.session_state.products.keys():
            st.caption(f"• {name}")
    else:
        st.info("暫無產品")
    
    st.markdown("---")
    
    # 已發送電郵
    if st.session_state.emails_sent:
        st.markdown("#### 📧 已發送電郵")
        st.markdown(f"**已發送: {len(st.session_state.emails_sent)} 封**")
        for email_log in st.session_state.emails_sent[-3:]:  # 顯示最後3封
            st.caption(f"📧 {email_log['to']} ({email_log['time']})")

# ========== 8. 主對話區域 ==========
st.markdown("### 💬 業務助手對話")

# 初始化秘書開場白
if not st.session_state.messages:
    initial_message = f"""
👋 您好！我是 CORA 業務秘書。歡迎使用完整版系統！

🎯 我可以協助您：
• **建立客戶資料** - 新客戶信息管理
• **管理產品目錄** - 產品資訊設置
• **生成銷售郵件** - 專業電郵撰寫
• **發送客戶聯絡** - 直接發送給客戶
• **業務分析建議** - 客戶洽詢策略

📋 請在左側邊欄添加您的客戶和產品資訊。然後告訴我您需要什麼幫助！

💡 例如，您可以問我：
• "幫我給 [客戶名] 寫一封推廣 [產品名] 的郵件"
• "我應該如何聯絡新客戶？"
• "幫我設計一個銷售追蹤計畫"
"""
    st.session_state.messages.append({
        "role": "assistant",
        "content": initial_message
    })

# 顯示對話歷史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ========== 9. 用戶輸入 & AI 回應 ==========
user_input = st.chat_input("💬 告訴我您需要什麼幫助...")

if user_input:
    # 添加用戶消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # 檢查是否要發送電郵
    should_send_email = "發送" in user_input or "email" in user_input.lower() or "郵件" in user_input
    
    with st.chat_message("assistant"):
        with st.spinner("🤔 思考中..."):
            # 構建上下文
            customers_info = json.dumps(st.session_state.customers, ensure_ascii=False, indent=2)
            products_info = json.dumps(st.session_state.products, ensure_ascii=False, indent=2)
            
            system_prompt = f"""
你是 CORA 業務秘書。你是一個專業的B2B銷售和客戶管理顧問。

公司信息：
{COMPANY_INFO}

當前客戶：
{customers_info if st.session_state.customers else "尚無客戶"}

當前產品：
{products_info if st.session_state.products else "尚無產品"}

重要指示：
1. 當用戶要求撰寫電郵時，生成專業、有說服力的商業電郵
2. 電郵應該包含：問候、公司介紹、產品價值主張、行動呼籲
3. 如果提到"發送"或"email"，在回覆結尾提醒用戶系統已準備好
4. 當用戶提供具體客戶或產品名稱時，使用該信息進行個性化建議
5. 對客戶管理、產品推廣、銷售策略提供專業建議

用戶問題：{user_input}

如果用戶要求生成電郵，按以下格式回覆：
---
📧 建議的電郵內容：

[郵件正文]
---
✉️ 該郵件已準備好發送。請確認收件人和內容無誤。
"""
            
            try:
                response = model.generate_content(system_prompt)
                assistant_message = response.text
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                st.markdown(assistant_message)
                
                # 如果要發送電郵，顯示發送按鈕
                if should_send_email and "---" in assistant_message:
                    st.markdown("---")
                    st.markdown("### 📧 電郵發送")
                    
                    # 提取郵件內容
                    email_content = assistant_message.split("---")[1].strip()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        recipient = st.selectbox(
                            "選擇收件人",
                            list(st.session_state.customers.keys()) if st.session_state.customers else []
                        )
                    
                    with col2:
                        email_subject = st.text_input("郵件主題", "來自 CORA 的商業提案")
                    
                    if recipient and st.button("✅ 發送電郵"):
                        recipient_email = st.session_state.customers[recipient]["email"]
                        
                        # 模擬發送（實際應用中連接真實郵件服務）
                        st.session_state.emails_sent.append({
                            "to": recipient,
                            "subject": email_subject,
                            "time": datetime.now().strftime("%H:%M")
                        })
                        
                        st.success(f"✅ 電郵已發送給 {recipient} ({recipient_email})")
                        st.info("💡 提示：在實際應用中，這將連接到您的郵件服務（SMTP）")
                        
                        # 記錄到對話
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"✅ 電郵成功發送給 {recipient}！\n\n發送時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n收件人：{recipient_email}\n主題：{email_subject}"
                        })
                        st.rerun()
                        
            except Exception as e:
                error_msg = f"❌ 出現問題：{str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# ========== 10. 清空對話 ==========
st.divider()
if st.button("🔄 清空對話"):
    st.session_state.messages = []
    st.rerun()
