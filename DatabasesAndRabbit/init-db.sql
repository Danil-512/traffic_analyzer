-- Создание таблицы для заблокированных IP
CREATE TABLE IF NOT EXISTS blocked_ips (
    id SERIAL PRIMARY KEY,
    ip_address INET NOT NULL UNIQUE,
    blocked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    pattern_matched VARCHAR(255),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Создание таблицы для логов подозрительных действий
CREATE TABLE IF NOT EXISTS suspicious_activities (
    id SERIAL PRIMARY KEY,
    ip_address INET NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    pattern_type VARCHAR(255),
    request_data JSONB,
    severity INTEGER DEFAULT 1
);

-- Создание индексов для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_blocked_ips_address ON blocked_ips(ip_address);
CREATE INDEX IF NOT EXISTS idx_blocked_ips_active ON blocked_ips(is_active);
CREATE INDEX IF NOT EXISTS idx_suspicious_activities_ip ON suspicious_activities(ip_address);
CREATE INDEX IF NOT EXISTS idx_suspicious_activities_time ON suspicious_activities(detected_at);
