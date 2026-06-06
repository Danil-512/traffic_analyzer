# api.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
from model_predict import SQLInjectionDetector

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка новой модели
detector = SQLInjectionDetector()

# Оптимальный порог для новой модели (подбираем на основе тестов)
# При 0.25 модель будет более чувствительной
SQL_THRESHOLD = 0.25

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'threshold': SQL_THRESHOLD,
        'model_loaded': True
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if not data or 'uri' not in data:
            return jsonify({'error': 'Missing uri field'}), 400
        
        # Получаем предсказание модели
        original_result = detector.predict(data)
        probability_sql = original_result['probability_sql']
        
        # Применяем порог
        is_injection = probability_sql >= SQL_THRESHOLD
        
        # Определяем уровень угрозы
        if probability_sql >= 0.7:
            threat = 'CRITICAL'
        elif probability_sql >= 0.5:
            threat = 'HIGH'
        elif probability_sql >= SQL_THRESHOLD:
            threat = 'MEDIUM'
        elif probability_sql >= 0.2:
            threat = 'LOW'
        else:
            threat = 'SAFE'
        
        result = {
            'is_sql_injection': is_injection,
            'threat_level': threat,
            'confidence': probability_sql if is_injection else 1-probability_sql,
            'probability_sql': probability_sql,
            'probability_normal': original_result['probability_normal'],
            'analyzed_uri': data.get('uri'),
            'threshold_used': SQL_THRESHOLD
        }
        
        if is_injection:
            logger.warning(f" SQL INJECTION! {data['uri'][:50]} (prob: {probability_sql:.3f})")
        else:
            logger.info(f" Normal: {data['uri'][:50]} (prob: {probability_sql:.3f})")
        
        return jsonify({'prediction': result})
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    try:
        data = request.json
        if not isinstance(data, list):
            return jsonify({'error': 'Expected array'}), 400
        
        results = []
        for log in data[:100]:  # Лимит 100 запросов
            original = detector.predict(log)
            prob = original['probability_sql']
            is_inj = prob >= SQL_THRESHOLD
            
            results.append({
                'uri': log.get('uri'),
                'is_sql_injection': is_inj,
                'probability_sql': prob,
                'threat_level': 'HIGH' if prob >= 0.5 else 'MEDIUM' if is_inj else 'SAFE'
            })
        
        return jsonify({'predictions': results, 'total': len(results)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def stats():
    return jsonify(detector.get_statistics())

@app.route('/test', methods=['GET'])
def test():
    """Тестовый эндпоинт для проверки модели"""
    test_queries = [
        ("/api/users?id=123", False),
        ("/api/users?id=1' OR '1'='1", True),
        ("/search?q=' UNION SELECT * FROM users", True),
        ("/login?username=admin", False),
        ("/login?username=admin'--", True),
    ]
    
    results = []
    for uri, expected in test_queries:
        pred = detector.predict({'uri': uri, 'status': 200})
        prob = pred['probability_sql']
        detected = prob >= SQL_THRESHOLD
        
        results.append({
            'uri': uri,
            'expected': expected,
            'detected': detected,
            'probability': prob,
            'correct': detected == expected
        })
    
    correct = sum(1 for r in results if r['correct'])
    return jsonify({
        'test_results': results,
        'summary': {
            'total': len(results),
            'correct': correct,
            'accuracy': f"{correct/len(results)*100:.1f}%",
            'threshold': SQL_THRESHOLD
        }
    })

if __name__ == '__main__':
    print("="*50)
    print(" SQL INJECTION DETECTOR API")
    print("="*50)
    print(f" Model loaded: YES")
    print(f"  Detection threshold: {SQL_THRESHOLD}")
    print(f" Server starting on http://0.0.0.0:5000")
    print("="*50)
    app.run(host='0.0.0.0', port=5000, debug=False)