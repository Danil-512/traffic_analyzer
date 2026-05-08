using AnalyzerService;

class Program
{
    static async Task Main(string[] args)
    {
        Console.WriteLine("=== Security Analyzer Service Starting ===");

        try
        {
            // 1. Инициализируем подключение к Redis 
            // Конструктор сам загрузит .env и создаст соединение
            var redisService = new RedisService();

            // 2. Создаем анализатор и передаем ему наш Redis
            var analyzer = new AnalyzerAllMethods(redisService);

            // 3. ПРИМЕР: Как это будет работать при получении данных
            // В реальности этот объект будет создаваться из JSON-лога Nginx
            var mockPacket = new Http
            {
                Ip = "192.168.1.50",
                Method = "POST",
                Path = "/api/login?step=1", // С параметрами, чтобы проверить нормализатор
                ResponseStatusCode = 401,
                UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                Referer = "http://your-site.com/login",
                RequestTime = 0.045,        // Время запроса (из Nginx)
                BodyBytesSent = 512,        // Размер ответа
                Payload = "admin' OR 1=1--" // Пример вредоносной нагрузки
            };

            // 4. Запускаем проверку
            string result = await analyzer.CheckBruteForce(mockPacket);

            Console.WriteLine($"Analysis result for {mockPacket.Ip}: {result}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"CRITICAL ERROR: {ex.Message}");
        }

        // Чтобы консоль не закрылась сразу
        Console.WriteLine("Press any key to exit...");
        Console.ReadKey();
    }
}
