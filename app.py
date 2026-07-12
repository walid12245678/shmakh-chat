import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from audio_recorder_streamlit import audio_recorder
from datetime import datetime

if not firebase_admin._apps:
    key_dict = st.secrets["firebase_key"]
    cred = credentials.Certificate(dict(key_dict))
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("💬 تطبيق الرسائل المطور")

# 1. التسجيل الصوتي
st.write("سجل مقطعاً صوتياً:")
audio_bytes = audio_recorder()
if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    st.success("تم تسجيل الصوت بنجاح!")

# 2. إرسال الرسائل النصية
user = st.text_input("اسـمك:")
message = st.text_input("رسالتك:")

if st.button("إرسال"):
    if user and message:
        db.collection("messages").add({
            "user": user,
            "text": message,
            "timestamp": datetime.now() # إضافة التاريخ والوقت
        })
        st.rerun()

# 3. عرض وحذف الرسائل
st.subheader("سجل الرسائل:")
messages = db.collection("messages").order_by("timestamp").stream()

for msg in messages:
    data = msg.to_dict()
    col1, col2 = st.columns([0.8, 0.2])
    
    with col1:
        time_str = data['timestamp'].strftime("%Y-%m-%d %H:%M") if 'timestamp' in data else ""
        st.write(f"({time_str}) 👤 **{data.get('user')}**: {data.get('text')}")
    
    with col2:
        if st.button("حذف", key=msg.id):
            db.collection("messages").document(msg.id).delete()
            st.rerun()