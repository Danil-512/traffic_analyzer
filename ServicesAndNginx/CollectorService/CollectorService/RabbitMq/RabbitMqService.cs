using System.Text;
using System.Collections.Generic;
using RabbitMQ.Client;
using System.Text.Json;

namespace CollectorService.RabbitMq
{
    public interface IRabbitMqService
    {
        void SendMessage(object obj);
        void SendMessage(string message);
    }

    public class RabbitMqService : IRabbitMqService
    {
        private readonly IConnection _connection;
        private readonly IModel _channel;

        public RabbitMqService()
        {
            // Определяем режим запуска
            var isDocker = Environment.GetEnvironmentVariable("DOCKER") == "Y";
            
            string rabbitHost;
            int rabbitPort;
            
            if (isDocker)
            {
                // Docker режим: используем RABBITMQ_DEFAULT_HOST
                rabbitHost = Environment.GetEnvironmentVariable("RABBITMQ_DEFAULT_HOST") ?? "172.17.0.1";
                rabbitPort = int.Parse(Environment.GetEnvironmentVariable("RABBITMQ_DEFAULT_PORT") ?? "5672");
                Console.WriteLine($"RabbitMQ (Docker mode): {rabbitHost}:{rabbitPort}");
            }
            else
            {
                // Локальный режим: используем REMOTE_DB_AND_RABBIT_HOST
                rabbitHost = Environment.GetEnvironmentVariable("REMOTE_DB_AND_RABBIT_HOST") ?? "localhost";
                rabbitPort = int.Parse(Environment.GetEnvironmentVariable("RABBITMQ_DEFAULT_PORT") ?? "5672");
                Console.WriteLine($"RabbitMQ (Local mode): {rabbitHost}:{rabbitPort}");
            }

            var factory = new ConnectionFactory
            {
                HostName = rabbitHost,
                Port = rabbitPort,
                UserName = Environment.GetEnvironmentVariable("RABBITMQ_DEFAULT_USER") ?? "guest",
                Password = Environment.GetEnvironmentVariable("RABBITMQ_DEFAULT_PASS") ?? "guest",
                VirtualHost = Environment.GetEnvironmentVariable("RABBITMQ_DEFAULT_VHOST") ?? "/"
            };

            _connection = factory.CreateConnection();
            _channel = _connection.CreateModel();

            // Объявление очереди
            _channel.QueueDeclare(
                queue: "analyzer.queue",
                durable: true,
                exclusive: false,
                autoDelete: false,
                arguments: new Dictionary<string, object>
                {
                    { "x-queue-type", "stream" }
                });
        }

        public void SendMessage(object obj)
        {
            var message = JsonSerializer.Serialize(obj);
            SendMessage(message);
        }

        public void SendMessage(string message)
        {
            var body = Encoding.UTF8.GetBytes(message);

            _channel.BasicPublish(
                exchange: "analyzer.events",
                routingKey: "log.analyzer",
                basicProperties: null,
                body: body);

            Console.WriteLine($"Message sent to RabbitMQ: {message}");
        }

        public void Dispose()
        {
            _channel?.Close();
            _connection?.Close();
        }
    }
}