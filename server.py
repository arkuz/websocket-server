from websocket_server import WebsocketServer
from random import randrange
import json

# список клиентов
clients_list = []


# Called for every client connecting (after handshake)
def new_client(client, server):
    print("New client connected and was given id %d" % client['id'])

    # инициализируем только что подключенного клиента
    client_info = {
        'id': hash(client['address']),
        'x': randrange(2001), #2001
        'y': randrange(2001),
    }

    # добавляем нового клиента в список клиентов
    flag = False
    for item in clients_list:
        if item['id'] == hash(client['address']):
            flag = True
            break
    if not flag:
        clients_list.append(client_info)

    # фомируем json для отправки
    full_info = {}
    full_info['me'] = client_info
    full_info['clients'] = clients_list
    print('new_client = ' + str(full_info))
    # отправляем клиенту его id, координаты и список всех клиентов
    full_info_json = json.dumps(full_info)
    server.send_message(client, full_info_json)


# Called for every client disconnecting
def client_left(client, server):
    print("Client(%d) disconnected" % client['id'])
    for item in clients_list:
        if item['id'] == hash(client['address']):
            clients_list.remove(item)
            disconnected = json.dumps({'disconnected': hash(client['address'])})
            server.send_message_to_all(disconnected)
            break


# Called when a client sends a message
def message_received(client, server, message):
    print("Client(%d) said: %s" % (client['id'], message))

    msg_dict = json.loads(message)

    # присваиваем имя
    new_client = None
    if 'name' in msg_dict:
        for item in clients_list:
            client_id = hash(client['address'])
            if item['id'] == client_id:
                new_client = item
                item['name'] = msg_dict['name']
                new_client = json.dumps({'new_client': new_client})
                server.send_message_to_all(new_client)
                break

    # принимаем координаты от клиента и обновляем их в списке клиентов
    if 'position' in msg_dict:
        for item in clients_list:
            client_id = hash(client['address'])
            if item['id'] == client_id:
                item['x'] = msg_dict['position']['x']
                item['y'] = msg_dict['position']['y']
                break

    # принимаем выстрел и отправляем его всем остальным
    if 'bullet_create' in msg_dict:
        msg_dict = msg_dict['bullet_create']
        bullet_create = {
            "id": msg_dict['id'],
            "dir": msg_dict['dir'],
            "speed": msg_dict['speed'],
            "x": msg_dict['x'],
            "y": msg_dict['y'],
        }
        bullet_create = json.dumps({'bullet_create': bullet_create})
        print(bullet_create)
        server.send_message_to_all(bullet_create)


    # принимаем столкновение и отправляем убитого игрока всем остальным
    if 'bullet_collision' in msg_dict:
        msg_dict = msg_dict['bullet_collision']
        for item in clients_list:
            if item['id'] == msg_dict['id']:
                if ((msg_dict['x'] >= item['x'] - msg_dict['width'] / 2) and (msg_dict['x'] <= item['x'] + msg_dict['width'] / 2)) and \
                        ((msg_dict['y'] >= item['y'] - msg_dict['height'] / 2) and (msg_dict['y'] <= item['y'] + msg_dict['height'] / 2)):
                    killed = json.dumps({'killed': msg_dict['id']})
                    print(killed)
                    server.send_message_to_all(killed)

                    #disconnected = json.dumps({'disconnected': msg_dict['id']})
                    #server.send_message_to_all(disconnected)

                    break


    # рассылаем список всех клиентов каждому клиенту
    client_list_json = json.dumps({'clients': clients_list})
    print(client_list_json)
    server.send_message_to_all(client_list_json)


PORT = 15000
HOST = '0.0.0.0'
print('Server run')
server = WebsocketServer(PORT, HOST)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()
