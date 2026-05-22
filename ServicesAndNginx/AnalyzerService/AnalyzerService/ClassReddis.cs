using StackExchange.Redis;
using DotNetEnv;
using System;
using System.IO;
using System.Threading.Tasks;

namespace AnalyzerService
{
    public class RedisService
    {
        private readonly IDatabase _db;
        private readonly ConnectionMultiplexer _redis;

        public RedisService()
        {
            // 1. Загружаем .env (твой блок кода)
            var envPaths = new[]
            {
                "../.env",
                ".env",
                "/app/.env"
            };

            bool envLoaded = false;
            foreach (var path in envPaths)
            {
                if (File.Exists(path))
                {
                    Env.Load(path);
                    Console.WriteLine($"Loaded .env from: {path}");
                    envLoaded = true;
                    break;
                }
            }

            if (!envLoaded)
            {
                Console.WriteLine("Warning: Using system/docker environment variables");
            }

            // 2. Читаем переменные именно с теми именами, что ты скинул
            string host = Environment.GetEnvironmentVariable("REDIS_HOST") ?? "localhost";
            string port = Environment.GetEnvironmentVariable("REDIS_PORT") ?? "6379";
            string password = Environment.GetEnvironmentVariable("REDIS_PASSWORD");

            // 3. Формируем строку подключения для StackExchange.Redis
            // Формат: "host:port,password=pass,abortConnect=false"
            string connectionString = $"{host}:{port},password={password},abortConnect=false";

            _redis = ConnectionMultiplexer.Connect(connectionString);
            _db = _redis.GetDatabase();
            Console.WriteLine($"Connected to Redis at {host}:{port}");
        }

        // Методы-обертки для анализатора
        public async Task<long> IncrementAsync(string key) => await _db.StringIncrementAsync(key);

        public async Task<bool> SetExpireAsync(string key, TimeSpan expiry) => await _db.KeyExpireAsync(key, expiry);

        public async Task<bool> DeleteAsync(string key) => await _db.KeyDeleteAsync(key);
    }
}
