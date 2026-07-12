import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import time

# 1. الاتصال بقاعدة البيانات (يبقى كما هو)
if not firebase_admin._apps:
    key_dict = st.secrets["firebase_key"]
    cred = credentials.Certificate(dict(key_dict))
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("💬 تطبيق الرسائل السحابي المباشر")

# 2. واجهة إدخال الرسائل
user = st.text_input("اسـمك:")
message = st.text_input("رسالتك:")

if st.button("إرسال"):
    if user and message:
        db.collection("messages").add({
            "user": user,
            "text": message,
            "timestamp": datetime.now()
        })
        st.rerun() # تحديث فوري بعد الإرسال
    else:
        st.warning("الرجاء كتابة الاسم والرسالة")

# 3. عرض الرسائل (نظام التحديث الذاتي)
st.subheader("سجل الرسائل:")
messages = db.collection("messages").order_by("timestamp").stream()

for msg in messages:
    data = msg.to_dict()
    time_str = data['timestamp'].strftime("%H:%M") if 'timestamp' in data else ""
    st.write(f"({time_str}) 👤 **{data.get('user', 'غير معروف')}**: {data.get('text', '')}")

# 4. التحديث التلقائي للصفحة (هذا الجزء يضيف ميزة التحديث كل 3 ثواني)
time.sleep(3) 
st.rerun()