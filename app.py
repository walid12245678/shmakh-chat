import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import hashlib

# --- إعدادات Firebase ---
if not firebase_admin._apps:
    key_dict = st.secrets["firebase_key"]
    cred = credentials.Certificate(dict(key_dict))
    firebase_admin.initialize_app(cred)
db = firestore.client()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- 1. إدارة تسجيل الدخول ---
if "username" not in st.session_state:
    st.session_state.username = None

if st.session_state.username is None:
    st.title("نظام الدردشة")
    choice = st.radio("العملية:", ["دخول", "حساب جديد"])
    user_input = st.text_input("اسم المستخدم:")
    password_input = st.text_input("كلمة المرور:", type="password")
    if st.button("تنفيذ"):
        user_ref = db.collection("users").document(user_input)
        doc = user_ref.get()
        if choice == "حساب جديد":
            if doc.exists: st.error("اليوزر مستخدم!")
            else:
                db.collection("users").document(user_input).set({"password": hash_password(password_input)})
                st.success("تم الإنشاء!")
        elif doc.exists and doc.to_dict().get("password") == hash_password(password_input):
            st.session_state.username = user_input
            st.rerun()
        else:
            st.error("بيانات خاطئة!")
    st.stop() # توقف هنا إذا لم يكن هناك مستخدم مسجل

# --- 2. واجهة التطبيق الرئيسية ---
st.title(f"مرحباً {st.session_state.username}")

# زر الخروج
if st.button("تسجيل خروج"):
    st.session_state.username = None
    st.rerun()

# القائمة الجانبية أو الرئيسية للدردشات
st.subheader("ابدأ محادثة جديدة")
new_target = st.text_input("اسم المستخدم الذي تريد مراسلته:")
if st.button("بدء محادثة"):
    if new_target:
        users_list = sorted([st.session_state.username, new_target])
        st.session_state.room_id = "_".join(users_list)
        st.session_state.target_user = new_target
        st.rerun()

# --- 3. منطقة المحادثة ---
if "room_id" in st.session_state:
    st.divider()
    st.subheader(f"الدردشة مع: {st.session_state.target_user}")
    
    # إرسال رسالة
    new_msg = st.text_input("اكتب رسالتك:", key="msg_input")
    if st.button("إرسال"):
        if new_msg:
            db.collection("messages").add({
                "room": st.session_state.room_id,
                "participants": [st.session_state.username, st.session_state.target_user],
                "sender": st.session_state.username,
                "text": new_msg,
                "timestamp": datetime.now()
            })
            st.rerun()

    # عرض الرسائل
    try:
        messages = db.collection("messages").where("room", "==", st.session_state.room_id).order_by("timestamp").stream()
        for msg in messages:
            data = msg.to_dict()
            st.write(f"**{data['sender']}**: {data['text']}")
    except Exception as e:
        st.error("حدث خطأ في عرض الرسائل، تأكد من الفهارس.")