import sqlite3
import ssl
import paho.mqtt.client as mqtt
import ast

ch = True

def gtogmc(grd, nore):
	otv = ''
	first = str(grd).split('.')
	otv += first[0] + '°'
	second = str(float('0.'+first[1])*60).split('.')
	otv += second[0]+"'"
	third = str(float('0.'+second[1])*60).split('.')
	otv += third[0]+'.'+third[1][0]+"''" + nore
	
	return otv

def on_subscribe(client, userdata, mid, granted_qos):
	print("Subscribed", client, userdata, mid, granted_qos)


def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print("Connected to broker")
		global Connected
		Connected = True
	else:
		print("Connection failed")

def on_message(client, userdata, message):
	con = sqlite3.connect('info.db')
	curs = con.cursor()
	#print(f"Message received: {message.payload}")
	listvar = {message.payload}
	listvar = eval(str(listvar)[3:-2])
	#print(listvar)
	cordx = listvar['current']['geo0']['lat'] - (listvar['current']['geo0']['lat'] - listvar['current']['geo1']['lat'])/2
	cordy = listvar['current']['geo0']['lon'] - (listvar['current']['geo0']['lon'] - listvar['current']['geo1']['lon'])/2
	#url1 = f"https://www.google.com/maps/place/{gtogmc(cordx,'N')}+{gtogmc(cordy,'E')}/@{listvar['current']['geo0']['lat']},{listvar['current']['geo0']['lon']},17z/data=!3m1!4b1!4m5!3m4!1s0x0:0x11b350a87beeb60b!8m2!3d{listvar['current']['geo0']['lat']}!4d{listvar['current']['geo0']['lon']}!5m1!1e4?hl=ru-RU"
	#url2 = f"https://www.google.com/maps/place/{gtogmc(cordx,'N')}+{gtogmc(cordy,'E')}/@{listvar['current']['geo1']['lat']},{listvar['current']['geo1']['lon']},17z/data=!3m1!4b1!4m5!3m4!1s0x0:0x11b350a87beeb60b!8m2!3d{listvar['current']['geo1']['lat']}!4d{listvar['current']['geo1']['lon']}!5m1!1e4?hl=ru-RU"
	url3 = f"https://2gis.ru/?m={cordy}%2C{cordx}%2F17&ruler={listvar['current']['geo0']['lon']}%2C{listvar['current']['geo0']['lat']}%7C{listvar['current']['geo1']['lon']}%2C{listvar['current']['geo1']['lat']}"
	#print(url1)
	#print(url2)
	#print(url3)
	if listvar['isWorking']:
		work = 'работает'
	else:
		work = 'не работает'
	if listvar['isWatering']:
		work += ', поливает'
	elif listvar['isWorking'] and not listvar['isWatering']:
		work += ', не поливает'
	curs.execute('DELETE FROM info')
	values = f'("{work}", "{listvar["current"]["geo0"]["lat"]}", "{listvar["current"]["geo0"]["lon"]}", "{listvar["current"]["geo1"]["lat"]}", "{listvar["current"]["geo1"]["lon"]}", "{gtogmc(listvar["current"]["geo0"]["lat"],"N")}", "{gtogmc(listvar["current"]["geo0"]["lon"],"E")}", "{gtogmc(listvar["current"]["geo1"]["lat"],"N")}", "{gtogmc(listvar["current"]["geo1"]["lon"],"E")}", "{url3}");'
	curs.execute('INSERT INTO info VALUES '+values)
	con.commit()
	#print(curs.execute('SELECT * FROM info').fetchall())
	con.close()

broker_address = "mqtt.cloud.yandex.net"
port = 8883
user = "aresmv64htqk8lkmqr61"
password = "ICLinnocamp2022"

client = mqtt.Client("kazanka")
client.username_pw_set(user, password=password)
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.tls_set(r"rootCA.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
client.tls_insecure_set(True)
client.connect(broker_address, port=port)
client.subscribe("$devices/are9gnqohp4npug37mbs/events/raw")

client.loop_forever()