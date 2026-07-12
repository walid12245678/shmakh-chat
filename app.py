import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import time

# 1. إعدادات الحماية (كلمة المرور)
password = st.sidebar.text_input("أدخل كلمة المرور للدخول:", type="password")

if password != "123456": # يمكنك تغيير "123456" إلى أي كلمة مرور تريدها
    st.warning("الرجاء إدخال كلمة المرور الصحيحة للوصول للتطبيق.")
    st.stop() # هذا الأمر يوقف تنفيذ باقي الكود إذا كانت كلمة المرور خطأ

# 2. الاتصال بقاعدة البيانات
if not firebase_admin._apps:
    key_dict = st.secrets["firebase_key"]
    cred = credentials.Certificate(dict(key_dict))
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("💬 تطبيق الرسائل السحابي المباشر")

# 3. واجهة إرسال الرسائل
user = st.text_input("اسـمك:")
message = st.text_input("رسالتك:")

if st.button("إرسال"):
    if user and message:
        db.collection("messages").add({
            "user": user,
            "text": message,
            "timestamp": datetime.now()
        })
        st.rerun()
    else:
        st.warning("الرجاء كتابة الاسم والرسالة")

# 4. عرض الرسائل
st.subheader("سجل الرسائل:")
messages = db.collection("messages").order_by("timestamp").stream()

for msg in messages:
    data = msg.to_dict()
    time_str = data['timestamp'].strftime("%H:%M") if 'timestamp' in data else ""
    st.write(f"({time_str}) 👤 **{data.get('user', 'غير معروف')}**: {data.get('text', '')}")

# 5. التحديث التلقائي
time.sleep(3) 
st.rerun()