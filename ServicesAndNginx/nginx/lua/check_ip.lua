local redis = require "resty.redis"
local red = redis:new()
red:set_timeout(500)

local redis_host = "172.17.0.1"
local redis_port = 6379
local redis_password = "dafej1@*jW"

local ok, err = red:connect(redis_host, redis_port)
if not ok then
    ngx.log(ngx.ERR, "Redis connection failed: ", err)
    return
end

if redis_password ~= "" then
    red:auth(redis_password)
end

-- Просмотр всех заголовков
local headers = ngx.req.get_headers()
ngx.log(ngx.WARN, "=== HEADERS ===")
ngx.log(ngx.WARN, "X-Forwarded-For: ", headers["X-Forwarded-For"] or "none")
ngx.log(ngx.WARN, "X-Real-IP: ", headers["X-Real-IP"] or "none")
ngx.log(ngx.WARN, "True-Client-IP: ", headers["True-Client-IP"] or "none")
ngx.log(ngx.WARN, "CF-Connecting-IP: ", headers["CF-Connecting-IP"] or "none")
ngx.log(ngx.WARN, "remote_addr: ", ngx.var.remote_addr)

-- Пытаемся определить реальный IP
local real_ip = headers["X-Forwarded-For"] or 
                headers["X-Real-IP"] or 
                headers["True-Client-IP"] or 
                headers["CF-Connecting-IP"] or 
                ngx.var.remote_addr

-- Если X-Forwarded-For содержит несколько IP, берем первый
if real_ip then
    real_ip = string.match(real_ip, "([^,]+)")
end

ngx.log(ngx.WARN, "Real IP detected: ", real_ip)

local is_blocked, err = red:sismember("blocked_ips", real_ip)
if err then
    ngx.log(ngx.ERR, "Redis error: ", err)
    return
end

if is_blocked == 1 then
    ngx.log(ngx.WARN, "!!! BLOCKED IP: ", real_ip)
    ngx.exit(ngx.HTTP_FORBIDDEN)
end

ngx.log(ngx.INFO, "IP allowed: ", real_ip)
red:set_keepalive(10000, 100)
