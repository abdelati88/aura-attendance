# استخدام نسخة بايثون خفيفة
FROM python:3.9-slim

# تحديد مسار العمل جوه السيرفر
WORKDIR /app

# نسخ ملف المكتبات وتسطيبها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع
COPY . .

# فتح بورت 8501 الخاص بـ Streamlit
EXPOSE 8501

# أمر تشغيل الأبلكيشن
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]