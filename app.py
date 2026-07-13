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

# --- تسجيل الدخول (كما هو) ---
if "username" not in st.session_state: st.session_state.username = None
if st.session_state.username is None:
    # ... (نفس كود تسجيل الدخول السابق) ...
    # (قم بوضع كود تسجيل الدخول هنا)
    st.stop()

st.title(f"مرحباً {st.session_state.username}")

# --- نظام قائمة الدردشات (مثل الواتساب) ---
st.subheader("دردشاتك")

# 1. جلب المحادثات التي شارك فيها المستخدم
chats_ref = db.collection("messages")
# هذا الاستعلام يبحث عن الرسائل التي فيها اسمك (لتبسيط القائمة)
my_chats = chats_ref.where("participants", "array_contains", st.session_state.username).stream()

# 2. عرض القائمة
rooms = set()
for chat in my_chats:
    rooms.add(chat.to_dict()["room"])

for room in rooms:
    other_user = room.replace(st.session_state.username, "").replace("_", "")
    if st.button(f"محادثة مع: {other_user}"):
        st.session_state.room_id = room
        st.session_state.target_user = other_user

# 3. فتح محادثة جديدة
st.divider()
new_target = st.text_input("محادثة جديدة مع:")
if st.button("بدء محادثة"):
    users_list = sorted([st.session_state.username, new_target])
    st.session_state.room_id = "_".join(users_list)
    st.session_state.target_user = new_target
    st.rerun()

# --- صفحة المحادثة (تظهر فقط عند اختيار غرفة) ---
if "room_id" in st.session_state:
    st.subheader(f"الدردشة مع {st.session_state.target_user}")
    
    # عرض الرسائل
    messages = db.collection("messages").where("room", "==", st.session_state.room_id).order_by("timestamp").stream()
    for msg in messages:
        data = msg.to_dict()
        st.write(f"**{data['sender']}**: {data['text']}")
    
    # إرسال رسالة
    new_msg = st.text_input("رسالة جديدة:", key="chat_input")
    if st.button("إرسال"):
        db.collection("messages").add({
            "room": st.session_state.room_id,
            "participants": [st.session_state.username, st.session_state.target_user],
            "sender": st.session_state.username,
            "text": new_msg,
            "timestamp": datetime.now()
        })
        st.rerun()