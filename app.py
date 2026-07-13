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

# --- دالة تشفير كلمة المرور ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- صفحة تسجيل الدخول ---
if "username" not in st.session_state:
    st.session_state.username = None

if st.session_state.username is None:
    st.subheader("نظام الدردشة - تسجيل الدخول")
    choice = st.radio("اختر العملية:", ["دخول", "حساب جديد"])
    user_input = st.text_input("اسم المستخدم:")
    password_input = st.text_input("كلمة المرور:", type="password")
    
    if st.button("تنفيذ"):
        user_ref = db.collection("users").document(user_input)
        doc = user_ref.get()
        
        if choice == "حساب جديد":
            if doc.exists:
                st.error("عذراً، هذا الاسم مستخدم!")
            else:
                db.collection("users").document(user_input).set({
                    "password": hash_password(password_input)
                })
                st.success("تم إنشاء الحساب، سجل دخولك الآن.")
        else:
            if doc.exists and doc.to_dict().get("password") == hash_password(password_input):
                st.session_state.username = user_input
                st.rerun()
            else:
                st.error("خطأ في اسم المستخدم أو كلمة المرور!")
    st.stop()

# --- واجهة الدردشة ---
st.title(f"مرحباً بك يا {st.session_state.username}")

# اختيار الشخص للمراسلة
target_user = st.text_input("أدخل اسم المستخدم الذي تريد مراسلته:")
if st.button("بدء المحادثة"):
    # دمج الاسمين لإنشاء معرف غرفة فريد (يتم ترتيبهما أبجدياً لتوحيد الغرفة للطرفين)
    users_list = sorted([st.session_state.username, target_user])
    room_id = "_".join(users_list)
    st.session_state.room_id = room_id
    st.session_state.target_user = target_user

# عرض المحادثة
if "room_id" in st.session_state:
    st.divider()
    st.subheader(f"محادثة مع: {st.session_state.target_user}")
    
    # إرسال رسالة
    msg = st.text_input("اكتب رسالتك:")
    if st.button("إرسال"):
        if msg:
            db.collection("messages").add({
                "room": st.session_state.room_id,
                "sender": st.session_state.username,
                "text": msg,
                "timestamp": datetime.now()
            })
            st.rerun()

    # عرض الرسائل
    chats = db.collection("messages").where("room", "==", st.session_state.room_id).order_by("timestamp").stream()
    for chat in chats:
        data = chat.to_dict()
        st.write(f"👤 **{data['sender']}**: {data['text']}")