docker exec -u 0 nginx_to_analyzer_container sh -c 'cat > /etc/nginx/lua/check_ip.lua << "EOF"
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

local client_ip = ngx.var.remote_addr
ngx.log(ngx.WARN, "Checking IP: ", client_ip)

-- Формируем ключ в формате blocked_ip:192.168.1.1
local blocked_key = "blocked_ip:" .. client_ip
local is_blocked, err = red:exists(blocked_key)

if err then
    ngx.log(ngx.ERR, "Redis exists error: ", err)
    return
end

if is_blocked == 1 then
    ngx.log(ngx.WARN, "!!! BLOCKED IP: ", client_ip, " (key: ", blocked_key, ")")
    ngx.exit(ngx.HTTP_FORBIDDEN)
end

ngx.log(ngx.INFO, "IP allowed: ", client_ip)
red:set_keepalive(10000, 100)
EOF'

docker compose restart nginx
