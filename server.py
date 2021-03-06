from websocket_server import WebsocketServer

from sys import platform
from random import randrange
import json
import logging

# список клиентов
clients_list = []

def get_client_id(client):
    #id = hash(client['address'])
    id = client['address'][1]
    return id

# Called for every client connecting (after handshake)
def new_client(client, server):
    print("New client connected and was given id %d" % client['id'])

    # инициализируем только что подключенного клиента
    client_info = {
        'id': get_client_id(client),
        'x': randrange(2001), #2001
        'y': randrange(2001),
    }
    print(client_info)

    # добавляем нового клиента в список клиентов
    flag = False
    for item in clients_list:
        if item['id'] == get_client_id(client):
            flag = True
            break
    if not flag:
        clients_list.append(client_info)

    # фомируем json для отправки
    full_info = {}
    full_info['me'] = client_info
    full_info['clients'] = clients_list
    # отправляем клиенту его id, координаты и список всех клиентов
    full_info_json = json.dumps(full_info)
    print(full_info)
    server.send_message(client, full_info_json)


# Called for every client disconnecting
def client_left(client, server):
    print("Client(%d) disconnected" % client['id'])
    for item in clients_list:
        if item['id'] == get_client_id(client):
            clients_list.remove(item)
            disconnected = json.dumps({'disconnected': get_client_id(client)})
            server.send_message_to_all(disconnected)
            break


# Called when a client sends a message
def message_received(client, server, message):
    print("Client(%d) said: %s" % (client['id'], message))

    try:
        msg_dict = json.loads(message)
    except ValueError:
        print('Error JSON: ' + str(message))
        return

    if not isinstance(msg_dict, dict):
        print('Error JSON: ' + str(message))
        return

    # присваиваем имя
    new_client = None
    if 'name' in msg_dict:
        for item in clients_list:
            client_id = get_client_id(client)
            if item['id'] == client_id:
                new_client = item
                item['name'] = msg_dict['name']
                new_client = json.dumps({'new_client': new_client})
                server.send_message_to_all(new_client)
                break

    # принимаем координаты от клиента и обновляем их в списке клиентов
    if 'position' in msg_dict:
        for item in clients_list:
            client_id = get_client_id(client)
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
            print(f"client_id: {msg_dict['id']} == item_id: {item['id']}")
            if item['id'] == msg_dict['id']:
                if ((msg_dict['x'] >= item['x'] - msg_dict['width'] / 2) and (msg_dict['x'] <= item['x'] + msg_dict['width'] / 2)) and \
                        ((msg_dict['y'] >= item['y'] - msg_dict['height'] / 2) and (msg_dict['y'] <= item['y'] + msg_dict['height'] / 2)):
                    clients_list.remove(item)
                    killed = json.dumps({'killed': msg_dict['id']})
                    print(killed)
                    server.send_message_to_all(killed)
                    break


    # рассылаем список всех клиентов каждому клиенту
    client_list_json = json.dumps({'clients': clients_list})
    print(client_list_json)
    server.send_message_to_all(client_list_json)




HOST = '127.0.0.1'
if "linux" in platform.lower():
    HOST = '0.0.0.0'

PORT = 15000

if __name__ == "__main__":
	print('Server run')
	server = WebsocketServer(PORT, HOST, logging.DEBUG)
	server.set_fn_new_client(new_client)
	server.set_fn_client_left(client_left)
	server.set_fn_message_received(message_received)
	server.run_forever()
