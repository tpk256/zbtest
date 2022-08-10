using System.Net.Sockets;
using System.Net;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;


class Program
    {
        static string ip = "192.168.221.183";
        static int port = 49001;
    static void Main(string[] args)
        {

            Dictionary<string, string> dict = new Dictionary<string, string>();
            dict.Add("state_app", "True");
            dict.Add("Additional_info", "Something");
            byte[] data = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(dict));
            IPEndPoint client = new IPEndPoint(IPAddress.Parse(ip), port);
            Socket socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            socket.Connect(client);
            socket.Send(data);
            socket.Close();
            



    }
    }
