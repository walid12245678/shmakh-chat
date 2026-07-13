import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
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

# --- إدارة تسجيل الدخول والحسابات ---
if "username" not in st.session_state:
    st.session_state.username = None

if st.session_state.username is None:
    st.subheader("مرحباً بك في نظام الشماخ")
    choice = st.radio("اختر العملية:", ["تسجيل دخول", "حساب جديد"])
    user_input = st.text_input("اسم المستخدم:")
    password_input = st.text_input("كلمة المرور:", type="password")
    
    if st.button("تنفيذ"):
        user_ref = db.collection("users").document(user_input)
        doc = user_ref.get()
        
        if choice == "حساب جديد":
            if doc.exists:
                st.error("عذراً، هذا اليوزر مستخدم بالفعل!")
            else:
                db.collection("users").document(user_input).set({
                    "username": user_input,
                    "password": hash_password(password_input),
                    "last_change": datetime.now()
                })
                st.success("تم إنشاء حسابك! يمكنك تسجيل الدخول الآن.")
        else:
            # تسجيل دخول (مع استثناء المدير)
            if user_input == "admin" and password_input == "Wa122458":
                st.session_state.username = "admin"
                st.rerun()
            elif doc.exists and doc.to_dict().get("password") == hash_password(password_input):
                st.session_state.username = user_input
                st.rerun()
            else:
                st.error("خطأ: اسم المستخدم أو كلمة المرور غير صحيحة!")
    st.stop()

# --- منطق الـ 7 أيام لتغيير الاسم ---
def check_name_change(username):
    user_ref = db.collection("users").document(username)
    doc = user_ref.get()
    if doc.exists:
        data = doc.to_dict()
        last_change = data.get("last_change")
        if last_change:
            last_change_dt = last_change.replace(tzinfo=None)
            if (datetime.now() - last_change_dt) < timedelta(days=7):
                return False, last_change_dt
    return True, None

# --- واجهة تغيير الاسم ---
st.write(f"أهلاً بك يا **{st.session_state.username}**")
if st.checkbox("تغيير اسم المستخدم"):
    new_name = st.text_input("الاسم الجديد:")
    if st.button("تأكيد التغيير"):
        can_change, last_date = check_name_change(st.session_state.username)
        if can_change:
            db.collection("users").document(st.session_state.username).set({
                "username": new_name,
                "password": hash_password("123456"), 
                "last_change": datetime.now()
            })
            st.session_state.username = new_name
            st.success("تم تغيير الاسم!")
            st.rerun()
        else:
            st.error(f"لا يمكنك تغيير الاسم إلا بعد مرور 7 أيام. آخر تغيير كان في: {last_date.strftime('%Y-%m-%d')}")

# --- نظام المحادثة ---
st.divider()
st.subheader("المحادثة")

# إرسال الرسالة
message = st.text_input("اكتب رسالتك هنا:")
if st.button("إرسال"):
    if message:
        db.collection("messages").add({
            "user": st.session_state.username,
            "text": message,
            "timestamp": datetime.now()
        })
        st.rerun()

# --- عرض الرسائل المحدث ---
if st.session_state.username == "admin":
    st.warning("أنت في وضع المدير: تشاهد جميع المحادثات.")
    chats = db.collection("messages").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
else:
    chats = db.collection("messages").where("user", "==", st.session_state.username).order_by("timestamp", direction=firestore.Query.DESCENDING).stream()

for chat in chats:
    data = chat.to_dict()
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(f"👤 **{data.get('user')}**: {data.get('text')}")
    with col2:
        if st.button("حذف", key=chat.id):
            db.collection("messages").document(chat.id).delete()
            st.rerun()