import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import time

# --- إعدادات الحماية ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    password = st.sidebar.text_input("أدخل كلمة المرور:", type="password")
    if password == "123456":
        st.session_state.logged_in = True
        st.rerun()
    else:
        st.warning("الرجاء إدخال كلمة المرور الصحيحة.")
        st.stop()

# --- إعدادات اسم المستخدم ---
if "username" not in st.session_state:
    st.session_state.username = None

# إذا كان المستخدم لم يحدد اسماً بعد
if st.session_state.username is None:
    new_name = st.text_input("أدخل اسمك (لن تتمكن من تغييره لمدة 7 أيام):")
    if st.button("تأكيد الاسم"):
        st.session_state.username = new_name
        st.session_state.change_date = datetime.now()
        st.rerun()
    st.stop()

# --- عرض واجهة الشات ---
st.write(f"أهلاً بك يا **{st.session_state.username}**")

# الاتصال بقاعدة البيانات
if not firebase_admin._apps:
    key_dict = st.secrets["firebase_key"]
    cred = credentials.Certificate(dict(key_dict))
    firebase_admin.initialize_app(cred)
db = firestore.client()

# إرسال الرسالة باستخدام الاسم المحفوظ تلقائياً
message = st.text_input("رسالتك:")
if st.button("إرسال"):
    if message:
        db.collection("messages").add({
            "user": st.session_state.username,
            "text": message,
            "timestamp": datetime.now()
        })
        st.rerun()

# عرض الرسائل
messages = db.collection("messages").order_by("timestamp").stream()
for msg in messages:
    data = msg.to_dict()
    st.write(f"👤 **{data.get('user')}**: {data.get('text')}")

time.sleep(3)
st.rerun()