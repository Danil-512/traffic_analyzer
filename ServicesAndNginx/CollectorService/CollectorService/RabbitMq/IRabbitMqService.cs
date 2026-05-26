using System;
using System.Collections.Generic;
using System.Text;

namespace AuthService
{
    public interface IRabbitMqService
    {
        Task SendMessage(object obj);
        Task SendMessage(string message);
    }
}
