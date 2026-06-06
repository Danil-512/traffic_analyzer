import pickle
import json
from typing import Dict, Any, List, Union
import numpy as np
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLInjectionDetector:
    """Сервис обнаружения SQL-инъекций"""
    
    def __init__(self, model_path: str = 'model.pkl', 
                 scaler_path: str = 'scaler.pkl',
                 feature_extractor_path: str = 'feature_extractor.pkl'):
        
        # Загрузка модели
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        logger.info(f"Модель загружена из {model_path}")
        
        # Загрузка скейлера
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
        logger.info(f"Скейлер загружен из {scaler_path}")
        
        # Загрузка feature extractor
        try:
            with open(feature_extractor_path, 'rb') as f:
                self.feature_extractor = pickle.load(f)
        except:
            from feature_extractor import SQLInjectionFeatureExtractor
            self.feature_extractor = SQLInjectionFeatureExtractor()
            logger.info("Feature extractor создан заново")
        
        self.prediction_history = []
    
    def predict(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Предсказание для одного лога"""
        try:
            # Извлечение признаков
            features = self.feature_extractor.extract_from_log(log_entry)
            
            # Масштабирование
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Предсказание
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            result = {
                'is_sql_injection': bool(prediction),
                'threat_level': self._get_threat_level(probabilities[1]),
                'confidence': float(probabilities[1] if prediction == 1 else probabilities[0]),
                'probability_sql': float(probabilities[1]),
                'probability_normal': float(probabilities[0]),
                'timestamp': datetime.now().isoformat(),
                'analyzed_uri': log_entry.get('uri', '')
            }
            
            # Сохраняем в историю
            self.prediction_history.append(result)
            
            # Логирование
            if prediction == 1:
                logger.warning(f"SQL инъекция обнаружена! URI: {log_entry.get('uri')}, Вероятность: {probabilities[1]:.3f}")
            else:
                logger.info(f"Нормальный запрос: {log_entry.get('uri')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при предсказании: {e}")
            return {
                'error': str(e),
                'is_sql_injection': False,
                'confidence': 0.0
            }
    
    def _get_threat_level(self, probability: float) -> str:
        """Определение уровня угрозы"""
        if probability >= 0.8:
            return 'CRITICAL'
        elif probability >= 0.6:
            return 'HIGH'
        elif probability >= 0.4:
            return 'MEDIUM'
        elif probability >= 0.2:
            return 'LOW'
        else:
            return 'SAFE'
    
    def predict_batch(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Пакетное предсказание с прогресс-баром"""
        results = []
        total = len(logs)
        
        for i, log in enumerate(logs):
            if i % 100 == 0:
                logger.info(f"Обработка: {i}/{total}")
            results.append(self.predict(log))
        
        # Статистика пакета
        threats = sum(1 for r in results if r['is_sql_injection'])
        logger.info(f"\n📊 Статистика пакета: {threats}/{total} запросов содержат SQL инъекции ({threats/total*100:.1f}%)")
        
        return results
    
    def analyze_from_nginx_log(self, nginx_log_line: str) -> Dict[str, Any]:
        """Анализ прямой строки лога nginx"""
        try:
            log_entry = json.loads(nginx_log_line.strip())
            return self.predict(log_entry)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return {'error': 'Invalid JSON format', 'is_sql_injection': False}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики предсказаний"""
        if not self.prediction_history:
            return {'total_predictions': 0}
        
        total = len(self.prediction_history)
        threats = sum(1 for p in self.prediction_history if p['is_sql_injection'])
        
        return {
            'total_predictions': total,
            'sql_injections_detected': threats,
            'detection_rate': threats / total if total > 0 else 0,
            'by_threat_level': {
                level: sum(1 for p in self.prediction_history if p.get('threat_level') == level)
                for level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'SAFE']
            }
        }
    
    def save_prediction_history(self, filepath: str = 'prediction_history.json'):
        """Сохранение истории предсказаний"""
        with open(filepath, 'w') as f:
            json.dump(self.prediction_history[-1000:], f, indent=2)  # Сохраняем последние 1000
        logger.info(f"История предсказаний сохранена в {filepath}")


# Пример использования
if __name__ == "__main__":
    # Инициализация детектора
    detector = SQLInjectionDetector()
    
    # Тестовые запросы
    test_logs = [
        {
            "uri": "/api/users?id=1",
            "method": "GET",
            "status": 200,
            "body": ""
        },
        {
            "uri": "/api/users?id=1' OR '1'='1",
            "method": "GET",
            "status": 200,
            "body": ""
        },
        {
            "uri": "/login",
            "method": "POST",
            "status": 200,
            "body": "username=admin&password=pass"
        }
    ]
    
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ДЕТЕКТОРА SQL ИНЪЕКЦИЙ")
    print("="*60)
    
    for log in test_logs:
        result = detector.predict(log)
        print(f"\n📝 URI: {log['uri']}")
        print(f"   Результат: {'🔴 SQL ИНЪЕКЦИЯ' if result['is_sql_injection'] else '✅ Нормальный'}")
        print(f"   Уровень угрозы: {result['threat_level']}")
        print(f"   Вероятность SQL: {result['probability_sql']:.3f}")
    
    # Статистика
    print("\n" + "="*60)
    print("СТАТИСТИКА")
    print("="*60)
    stats = detector.get_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))