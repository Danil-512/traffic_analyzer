-- check_ip.lua
-- Проверка IP в Redis перед обработкой запроса

local redis = require "resty.redis"
local cjson = require "cjson"

local red = redis:new()
red:set_timeout(500) -- 500 мс таймаут на соединение с Redis

-- Подключение к Redis
local redis_host = os.getenv("REDIS_HOST") or "redis"
local redis_port = os.getenv("REDIS_PORT") or 6379

local ok, err = red:connect(redis_host, redis_port)
if not ok then
    -- Если Redis недоступен - пропускаем запрос (не блокируем)
    ngx.log(ngx.WARN, "Redis connection failed: ", err)
    return
end

-- Получаем IP клиента
local client_ip = ngx.var.remote_addr

-- Проверяем, есть ли IP в множестве blocked_ips
local is_blocked, err = red:sismember("blocked_ips", client_ip)

if err then
    ngx.log(ngx.ERR, "Redis sismember error: ", err)
    return
end

-- Если IP заблокирован - возвращаем 403
if is_blocked == 1 then
    ngx.log(ngx.WARN, "Blocked IP: ", client_ip)
    ngx.exit(ngx.HTTP_FORBIDDEN)
end

-- Если не заблокирован - продолжаем обработку
red:set_keepalive(10000, 100) -- Пул соединений Redis