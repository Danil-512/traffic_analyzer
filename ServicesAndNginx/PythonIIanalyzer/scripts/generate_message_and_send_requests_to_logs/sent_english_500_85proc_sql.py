#!/usr/bin/env python3
# send_sql_injections.py

import csv
import requests
import time
import json
from typing import List, Dict

class SQLInjectionSender:
    """Отправка запросов с SQL-инъекциями"""
    
    def __init__(self):
        self.base_url = "https://tchk.site"
        self.session = requests.Session()
        
        self.headers = {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/register",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "DNT": "1"
        }
    
    def send_register_request(self, message_text: str, index: int, is_injection: bool) -> Dict:
        """Отправка запроса на регистрацию с текстом инъекции"""
        url = f"{self.base_url}/api/Auth/send-verification"
        
        # Для инъекций используем специальную метку в username
        prefix = "inj" if is_injection else "nor"
        clean_text = message_text[:35].replace(' ', '_').replace('"', '').replace("'", '').replace('\n', '')
        
        payload = {
            "username": f"{prefix}_{clean_text}_{index}"[:50],
            "email": f"{prefix}_{index}@test.com",
            "password": "InjectionTest123!",
            "device_info": "web"
        }
        
        try:
            response = self.session.post(url, json=payload, headers=self.headers, timeout=5)
            return {
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "message_text": message_text,
                "is_injection": is_injection,
                "index": index
            }
        except Exception as e:
            return {
                "status_code": 0,
                "success": False,
                "error": str(e),
                "message_text": message_text,
                "is_injection": is_injection,
                "index": index
            }
    
    def load_messages(self, csv_file: str) -> List[Dict]:
        """Загрузка сообщений из датасета"""
        messages = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                messages.append({
                    "text": row['text'],
                    "is_injection": row['is_injection'] == 'True',
                    "message_type": row.get('message_type', 'unknown')
                })
        return messages
    
    def send_all(self, messages: List[Dict], delay: float = 0.05):
        """Отправка всех сообщений"""
        
        total = len(messages)
        injection_count = sum(1 for m in messages if m['is_injection'])
        
        print(f"\n🚀 Отправка {total} сообщений...")
        print(f"   SQL-инъекции: {injection_count} ({injection_count/total*100:.1f}%)")
        print(f"   Нормальные: {total - injection_count}")
        print("=" * 70)
        
        results = []
        success_count = 0
        injection_success = 0
        
        for i, msg in enumerate(messages):
            result = self.send_register_request(msg['text'], i, msg['is_injection'])
            results.append(result)
            
            if result['status_code'] == 200:
                success_count += 1
                if msg['is_injection']:
                    injection_success += 1
            
            # Прогресс каждые 50 сообщений
            if (i + 1) % 50 == 0 or i == total - 1:
                msg_type = "🔴INJ" if msg['is_injection'] else "🟢NOR"
                status = "✅" if result['status_code'] == 200 else "❌"
                percent = ((i + 1) / total) * 100
                print(f"{status} [{i+1:3}/{total}] {percent:5.1f}% | {msg_type} | {msg['text'][:45]}... | HTTP {result['status_code']}")
            
            time.sleep(delay)
        
        # Статистика
        print("\n" + "=" * 70)
        print("📊 СТАТИСТИКА ОТПРАВКИ:")
        print(f"  Всего запросов: {total}")
        print(f"  Успешно (200): {success_count} ({(success_count/total)*100:.1f}%)")
        print(f"  SQL-инъекций отправлено: {injection_count}")
        print(f"  SQL-инъекций успешно: {injection_success} ({(injection_success/injection_count)*100:.1f}% если injection_count > 0 else 0)")
        print(f"  Ошибок: {total - success_count}")
        
        return results

def main():
    print("=" * 70)
    print("ОТПРАВКА SQL-ИНЪЕКЦИЙ (500 сообщений, 85% инъекций)")
    print("=" * 70)
    
    sender = SQLInjectionSender()
    
    # Загружаем датасет
    print("\n📥 Загрузка сообщений из sql_injections_85percent.csv...")
    messages = sender.load_messages("sql_injections_85percent.csv")
    
    if not messages:
        print("❌ Файл sql_injections_85percent.csv не найден!")
        print("   Сначала запустите: python3 generate_sql_injections.py")
        return
    
    injection_count = sum(1 for m in messages if m['is_injection'])
    print(f"✅ Загружено {len(messages)} сообщений")
    print(f"  SQL-инъекции: {injection_count} ({injection_count/len(messages)*100:.1f}%)")
    print(f"  Нормальные: {len(messages) - injection_count}")
    
    # Подтверждение
    print(f"\n⚠️  Будет отправлено {len(messages)} запросов на сервер")
    print(f"  Из них {injection_count} содержат SQL-инъекции")
    confirm = input("Продолжить? (y/N): ")
    if confirm.lower() != 'y':
        print("Отменено")
        return
    
    # Отправка
    results = sender.send_all(messages, delay=0.05)
    
    # Сохраняем результаты
    with open('send_results_injections_500.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n✅ Результаты сохранены в send_results_injections_500.json")
    print("\n📋 Для просмотра логов на сервере:")
    print("  tail -f ~/Git/Messenger/logs/access.log")

if __name__ == "__main__":
    main()
