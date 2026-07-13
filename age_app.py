import streamlit as st
from datetime import datetime

st.title("حاسبة العمر بالكتابة")

# خانة للكتابة
birth_input = st.text_input("أدخل تاريخ ميلادك بهذا التنسيق (سنة-شهر-يوم):", "2004-09-05")

if st.button("احسب عمري"):
    try:
        birth_date = datetime.strptime(birth_input, "%Y-%m-%d").date()
        today = datetime.today().date()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        st.success(f"عمرك الآن هو: {age} سنة")
    except:
        st.error("خطأ في التنسيق! تأكد من كتابة التاريخ مثل: 2004-09-05")

# إضافة اسم المطور في أسفل الصفحة
st.markdown("---") # هذا السطر يرسم خطاً فاصلاً
st.write("تم التطوير بواسطة: **وليد الشماخ**")
