# scripts/test_model.py
import json
import sys
from pathlib import Path

# Добавляем родительскую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

from model_predict import SQLInjectionDetector

def test_with_real_data():
    """Тестирование на реальных данных"""
    detector = SQLInjectionDetector()
    
    # Тестовые запросы из ваших датасетов
    test_cases = [
        # Нормальные запросы
        ("/api/users?id=123", "GET", 200, False),
        ("/products?category=electronics", "GET", 200, False),
        ("/login", "POST", 200, False),
        
        # SQL инъекции
        ("/api/users?id=1' OR '1'='1", "GET", 200, True),
        ("/login?user=admin'--", "POST", 403, True),
        ("/search?q=' UNION SELECT * FROM users--", "GET", 500, True),
    ]
    
    print("="*70)
    print("ТЕСТИРОВАНИЕ ДЕТЕКТОРА НА ТЕСТОВЫХ ДАННЫХ")
    print("="*70)
    
    correct = 0
    for uri, method, status, expected in test_cases:
        result = detector.predict({
            'uri': uri,
            'method': method,
            'status': status,
            'body': ''
        })
        
        is_correct = result['is_sql_injection'] == expected
        correct += is_correct
        
        status_icon = "✅" if is_correct else "❌"
        prediction = "🔴 SQL" if result['is_sql_injection'] else "🟢 NORMAL"
        expected_str = "SQL" if expected else "NORMAL"
        
        print(f"{status_icon} {prediction} (Expected: {expected_str}) | Confidence: {result['confidence']:.3f} | URI: {uri[:50]}")
    
    accuracy = correct / len(test_cases)
    print(f"\n📊 Точность на тестовом наборе: {accuracy*100:.1f}% ({correct}/{len(test_cases)})")

if __name__ == "__main__":
    test_with_real_data()