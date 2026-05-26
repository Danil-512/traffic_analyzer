using CollectorService.RabbitMq;

namespace CollectorService
{
    public class Worker : BackgroundService
    {
        private readonly ILogger<Worker> _logger;
        private readonly IRabbitMqService _rabbitMqService;

        public Worker(ILogger<Worker> logger, IRabbitMqService rabbitMqService)
        {
            _logger = logger;
            _rabbitMqService = rabbitMqService;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            _logger.LogInformation("Collector Worker Service started");

            // Отправка тестового сообщения при старте
            _rabbitMqService.SendMessage(new
            {
                timestamp = DateTime.UtcNow,
                message = "Collector Service started",
                status = "running",
                dockerMode = Environment.GetEnvironmentVariable("DOCKER") == "Y"
            });

            while (!stoppingToken.IsCancellationRequested)
            {
                // Здесь будет основная логика приема логов
                await Task.Delay(10000, stoppingToken);
            }
        }
    }
}