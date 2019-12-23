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
		# 'address': client['address'][0],
		# 'port': client['address'][1],
		'x': randrange(2001),
		'y': randrange(2001),
	}

	# добавляем нового клиента в список клиентов
	if not clients_list:
		clients_list.append(client_info)
	else:
		flag = False
		for item in clients_list:
			#if item['address'] == client['address'][0] and item['port'] == client['address'][1]:
			if item['id'] == hash(client['address']):
				flag = True
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
		#if item['address'] == client['address'][0] and item['port'] == client['address'][1]:
		if item['id'] == hash(client['address']):
			clients_list.remove(item)


# Called when a client sends a message
def message_received(client, server, message):
	print("Client(%d) said: %s" % (client['id'], message))

	# принимаем координаты от клиента и обновляем их в списке клиентов
	msg_dict = json.loads(message)
	for item in clients_list:
		client_id = hash(client['address'])
		if item['id'] == client_id:
			item['x'] = msg_dict['x']
			item['y'] = msg_dict['y']

	# рассылаем список всех клиентов каждому клиенту
	print(clients_list)
	client_list_json = json.dumps(clients_list)
	server.send_message_to_all(client_list_json)


PORT=15000
print('Server run')
server = WebsocketServer(PORT)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()

