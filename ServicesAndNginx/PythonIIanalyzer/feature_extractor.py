import re
import json
from typing import Dict, Any, List
import numpy as np

class SQLInjectionFeatureExtractor:
    """Извлечение признаков для обнаружения SQL-инъекций"""
    
    # Расширенные паттерны SQL-инъекций
    SQL_PATTERNS = {
        'union': r'\bUNION\b.*\bSELECT\b',
        'or_condition': r"'?\s+OR\s+['\"]?\s*=|OR\s+\d+=\d+|OR\s+1=1",
        'and_condition': r"'?\s+AND\s+['\"]?\s*=|AND\s+\d+=\d+",
        'comment': r'--|\#|\/\*|\*\/',
        'semicolon': r';',
        'select': r'\bSELECT\b',
        'insert': r'\bINSERT\b',
        'update': r'\bUPDATE\b',
        'delete': r'\bDELETE\b',
        'drop': r'\bDROP\b',
        'sleep': r'\bSLEEP\b|BENCHMARK|pg_sleep|WAITFOR\s+DELAY',
        'information_schema': r'information_schema|sys\.|master\.\.',
        'union_select': r'UNION\s+SELECT',
        'xp_cmdshell': r'xp_cmdshell|sp_executesql|sp_configure',
        'exec': r'\bEXEC\b|EXECUTE|\bCALL\b',
        'boolean_blind': r"'?\s+AND\s+'\w+'='\w+|'?\s+OR\s+'\w+'='\w+",
        'time_based': r'WAITFOR\s+DELAY|SLEEP\(\d+\)|pg_sleep\(\d+\)',
        'error_based': r'CONVERT\(|CAST\(|EXTRACTVALUE|UPDATEXML',
        'stacked_queries': r';.*?(DROP|DELETE|INSERT|UPDATE|CREATE)',
        'encoding_attempt': r'%27|%22|%3B|%2F\*|%\d{2}',  # URL encoded attacks
        'hex_encoding': r'0x[0-9A-Fa-f]{2,}',
        'union_all': r'UNION\s+ALL\s+SELECT',
        'order_by': r'ORDER\s+BY\s+\d+',
        'into_outfile': r'INTO\s+(OUTFILE|DUMPFILE)',
    }
    
    # Специальные символы SQL
    SQL_SPECIAL_CHARS = ["'", '"', ';', '--', '#', '/*', '*/', '(', ')', '=', '>', '<', '`', '%', '_']
    
    def __init__(self):
        self.compiled_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.SQL_PATTERNS.items()
        }
    
    def extract_from_log(self, log_entry: Dict[str, Any]) -> np.ndarray:
        """Извлечение признаков из записи лога"""
        features = []
        
        # Извлечение URI и тела запроса
        uri = log_entry.get('uri', '')
        body = log_entry.get('body', '')
        full_request = f"{uri} {body}".lower()
        
        # 1. Бинарные признаки наличия SQL-паттернов
        for pattern_name, pattern in self.compiled_patterns.items():
            features.append(1 if pattern.search(full_request) else 0)
        
        # 2. Количество специальных символов (нормализованное)
        special_chars_count = sum(full_request.count(char) for char in self.SQL_SPECIAL_CHARS)
        features.append(min(special_chars_count / 30, 1))
        
        # 3. Длина запроса (нормализованная)
        features.append(min(len(full_request) / 1000, 1))
        
        # 4. Количество пробелов (признак сложного запроса)
        space_count = full_request.count(' ')
        features.append(min(space_count / 100, 1))
        
        # 5. Наличие шестнадцатеричных последовательностей
        has_hex = 1 if re.search(r'0x[0-9A-Fa-f]+', full_request) else 0
        features.append(has_hex)
        
        # 6. Количество операторов сравнения
        operators = ['=', '>', '<', '<=', '>=', '!=']
        operators_count = sum(full_request.count(op) for op in operators)
        features.append(min(operators_count / 15, 1))
        
        # 7. Статус ответа (если есть ошибка SQL)
        status = log_entry.get('status', 200)
        error_statuses = [400, 403, 404, 500, 502, 503]
        features.append(1 if status in error_statuses else 0)
        
        # 8. Отношение специальных символов к длине
        if len(full_request) > 0:
            special_ratio = special_chars_count / len(full_request)
        else:
            special_ratio = 0
        features.append(min(special_ratio, 1))
        
        # 9. Количество числовых значений в запросе
        numbers_count = len(re.findall(r'\d+', full_request))
        features.append(min(numbers_count / 20, 1))
        
        # 10. Наличие подозрительных ключевых слов
        suspicious_keywords = ['password', 'pass', 'user', 'admin', 'login', 'credential']
        has_suspicious = 1 if any(keyword in full_request for keyword in suspicious_keywords) else 0
        features.append(has_suspicious)
        
        return np.array(features, dtype=np.float32)
    
    def get_feature_names(self) -> List[str]:
        """Возвращает имена признаков"""
        names = list(self.SQL_PATTERNS.keys())
        names.extend([
            'special_chars_ratio',
            'request_length',
            'space_count',
            'has_hex',
            'operators_count',
            'is_error_status',
            'special_to_length_ratio',
            'numbers_count',
            'has_suspicious_keywords'
        ])
        return names
    
    def get_feature_count(self) -> int:
        """Возвращает количество признаков"""
        return len(self.get_feature_names())