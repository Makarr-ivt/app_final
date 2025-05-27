import os
import django
from django.conf import settings
from django.contrib.auth.hashers import make_password

# Настраиваем Django
settings.configure(
    DATABASES={},
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
    ]
)
django.setup()

# Пароли для хеширования
passwords = {
    'anna.petrova@example.com': 'manager123',
    'ivan.sidorov@example.com': 'manager456',
    'maria.ivanova@example.com': 'worker123',
    'alexey.smirnov@example.com': 'worker456',
    'elena.kozlova@example.com': 'worker789'
}

print("-- Хеши паролей для SQL скрипта:")
for email, password in passwords.items():
    hashed = make_password(password)
    print(f"-- Для {email} (пароль: {password})")
    print(f"-- {hashed}")
    print() 