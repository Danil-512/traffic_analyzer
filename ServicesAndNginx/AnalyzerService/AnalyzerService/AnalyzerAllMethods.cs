using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks; // Нужно для Task


namespace AnalyzerService
{
    public class AnalyzerAllMethods
    {
        // 1. Поля класса должны быть ВНУТРИ фигурных скобок класса
        private readonly RedisService _redis;

        // МЕНЯЕМ: Конструктор теперь принимает RedisService
        public AnalyzerAllMethods(RedisService redis)
        {
            _redis = redis;
        }

        private static readonly System.Text.RegularExpressions.Regex WhitespaceRegex =
            new System.Text.RegularExpressions.Regex(@"\s+", System.Text.RegularExpressions.RegexOptions.Compiled);

        // 2. Метод Normalize (инструмент)
        private string Normalize(string input)
        {
            if (string.IsNullOrEmpty(input)) return string.Empty;

            string result = input;
            string decoded = System.Net.WebUtility.UrlDecode(result);
            while (decoded != result)
            {
                result = decoded;
                decoded = System.Net.WebUtility.UrlDecode(result);
            }

            result = System.Net.WebUtility.HtmlDecode(result);
            result = result.ToLower();

            int questionMarkIndex = result.IndexOf('?');
            if (questionMarkIndex != -1)
            {
                result = result.Substring(0, questionMarkIndex);
            }

            result = result.Replace("\0", "");
            result = WhitespaceRegex.Replace(result, " ");

            return result.Trim();
        }

        // 3. Метод Брутфорса (логика)
        public async Task<string> CheckBruteForce(Http packet)
        {
            string cleanPath = Normalize(packet.Path);

            if (packet.Method == "POST" && cleanPath == "/api/login")
            {
                if (packet.ResponseStatusCode == 401 || packet.ResponseStatusCode == 403)
                {
                    string redisKey = $"bf:{packet.Ip}";

                    long attempts = await _redis.IncrementAsync(redisKey);
                    await _redis.SetExpireAsync(redisKey, TimeSpan.FromHours(24));

                    if (attempts >= 15) return "BAN";
                    if (attempts >= 5) return "CAPTCHA";

                    return "LOG_ATTEMPT";
                }

                if (packet.ResponseStatusCode == 200)
                {
                    await _redis.DeleteAsync($"bf:{packet.Ip}");
                    return "CLEAN";
                }
            }

            return "SKIP";
        }
    }
}
