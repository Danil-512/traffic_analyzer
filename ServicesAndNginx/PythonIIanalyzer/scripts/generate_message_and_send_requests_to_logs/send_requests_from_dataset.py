#!/usr/bin/env python3
# correct_registration.py

import requests
import json
import random
import time
import csv
from typing import Dict, List

class MessengerClient:
    def __init__(self):
        self.base_url = "https://tchk.site"
        self.session = requests.Session()
        
        self.headers = {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/register",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*"
        }
    
    def send_verification(self, username: str, email: str, password: str) -> Dict:
        """Шаг 1: Отправка verification code на email"""
        url = f"{self.base_url}/api/Auth/send-verification"
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "device_info": "web"
        }
        
        response = self.session.post(url, json=payload, headers=self.headers, timeout=10)
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.json() if response.text else {},
            "payload": payload
        }
    
    def verify_code(self, email: str, code: str) -> Dict:
        """Шаг 2: Подтверждение verification code"""
        url = f"{self.base_url}/api/Auth/verify-code"
        payload = {
            "email": email,
            "code": code
        }
        
        response = self.session.post(url, json=payload, headers=self.headers, timeout=10)
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.json() if response.text else {}
        }
    
    def register_complete(self, email: str, code: str, username: str, password: str) -> Dict:
        """Шаг 3: Полная регистрация после верификации"""
        url = f"{self.base_url}/api/Auth/register"
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "verificationCode": code
        }
        
        response = self.session.post(url, json=payload, headers=self.headers, timeout=10)
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.json() if response.text else {}
        }
    
    def resend_code(self, email: str) -> Dict:
        """Повторная отправка кода"""
        url = f"{self.base_url}/api/Auth/resend-verification"
        payload = {"email": email}
        
        response = self.session.post(url, json=payload, headers=self.headers, timeout=10)
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.json() if response.text else {}
        }
    
    def login(self, email: str, password: str) -> Dict:
        """Логин после регистрации"""
        url = f"{self.base_url}/api/Auth/login"
        payload = {
            "email": email,
            "password": password
        }
        
        response = self.session.post(url, json=payload, headers=self.headers, timeout=10)
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.json() if response.text else {},
            "token": response.json().get('token') if response.text else None
        }
    
    def send_message(self, token: str, chat_id: int, message: str) -> Dict:
        """Отправка сообщения в чат"""
        url = f"{self.base_url}/api/Chat/messages"
        payload = {
            "chatId": chat_id,
            "content": message,
            "type": "text"
        }
        
        headers = self.headers.copy()
        headers["Authorization"] = f"Bearer {token}"
        
        response = self.session.post(url, json=payload, headers=headers, timeout=10)
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.json() if response.text else {}
        }
    
    def complete_registration_flow(self, username: str, email: str, password: str, verification_code: str = None):
        """Полный цикл регистрации"""
        
        print(f"\n📝 Регистрация пользователя: {username}")
        print(f"📧 Email: {email}")
        
        # Шаг 1: Отправка кода
        print("  Шаг 1: Отправка verification code...")
        send_result = self.send_verification(username, email, password)
        
        if not send_result['success']:
            print(f"    ❌ Ошибка: {send_result.get('response', {}).get('message', 'Unknown')}")
            return None
        
        print(f"    ✅ Код отправлен на {email}")
        
        # Шаг 2: Верификация (если код не передан, нужно получить из email)
        if verification_code:
            print(f"  Шаг 2: Верификация с кодом {verification_code}...")
            verify_result = self.verify_code(email, verification_code)
            
            if not verify_result['success']:
                print(f"    ❌ Ошибка верификации: {verify_result.get('response', {}).get('message', 'Unknown')}")
                return None
            
            print(f"    ✅ Email подтвержден")
            
            # Шаг 3: Полная регистрация
            print(f"  Шаг 3: Завершение регистрации...")
            register_result = self.register_complete(email, verification_code, username, password)
            
            if not register_result['success']:
                print(f"    ❌ Ошибка: {register_result.get('response', {}).get('message', 'Unknown')}")
                return None
            
            print(f"    ✅ Регистрация завершена!")
            
            # Шаг 4: Логин
            print(f"  Шаг 4: Авторизация...")
            login_result = self.login(email, password)
            
            if login_result['success']:
                print(f"    ✅ Успешный вход!")
                return login_result.get('token')
            else:
                print(f"    ❌ Ошибка входа: {login_result.get('response', {}).get('message', 'Unknown')}")
                return None
        else:
            print(f"  ⚠️ Требуется ввод verification code из email")
            print(f"  Используйте команду: verify_code('{email}', 'код_из_письма')")
            return None

def main():
    print("=" * 70)
    print("КЛИЕНТ МЕССЕНДЖЕРА (С РАБОЧИМ API)")
    print("=" * 70)
    
    client = MessengerClient()
    
    # Тестовая регистрация
    username = f"testuser_{random.randint(10000, 99999)}"
    email = f"{username}@test.com"
    password = "Test123456!"
    
    # Отправляем verification code
    result = client.send_verification(username, email, password)
    
    print(f"\n📊 Результат отправки кода:")
    print(f"  Статус: {result['status_code']}")
    print(f"  Успех: {result['success']}")
    print(f"  Ответ: {json.dumps(result['response'], ensure_ascii=False, indent=2)}")
    
    print("\n" + "=" * 70)
    print("💡 Дальнейшие действия:")
    print("1. Проверьте почту (в т.ч. спам) на наличие verification code")
    print("2. Запустите верификацию:")
    print(f"   client.verify_code('{email}', 'КОД_ИЗ_ПИСЬМА')")
    print("3. Затем завершите регистрацию и получите токен")

if __name__ == "__main__":
    main()
