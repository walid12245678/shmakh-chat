import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import os

# الاتصال بقاعدة البيانات
if not firebase_admin._apps:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    key_path = os.path.join(current_dir, "key.json")
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("💬 تطبيق الرسائل السحابي")

# واجهة إدخال الرسائل
user = st.text_input("اسـمك:")
message = st.text_input("رسالتك:")

if st.button("إرسال"):
    if user and message:
        db.collection("messages").add({
            "user": user,
            "text": message,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        st.success("تم إرسال رسالتك للسحابة!")
        st.rerun() # تحديث الصفحة لرؤية الرسالة الجديدة
    else:
        st.warning("الرجاء كتابة الاسم والرسالة")

# عرض الرسائل السابقة
st.subheader("سجل الرسائل:")
messages = db.collection("messages").order_by("timestamp").stream()

for msg in messages:
    data = msg.to_dict()
    st.write(f"👤 **{data.get('user', 'غير معروف')}**: {data.get('text', '')}")