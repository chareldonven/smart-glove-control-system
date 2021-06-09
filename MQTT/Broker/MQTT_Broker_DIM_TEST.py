import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from app import SensorMessageQueue, SmartGloveControlSystem

MQTT_ADDRESS = '192.168.178.100'
MQTT_USER = 'mosquitto'
MQTT_PASSWORD = 'mosquitto'
MQTT_TOPIC_BUTTON_SUB = '/esp32/button'
MQTT_TOPIC_FLEX_SUB = '/esp32/flex'
MQTT_TOPIC_BUTTON_PUB = '/esp8266/button'
MQTT_TOPIC_FLEX_PUB = '/esp8266/flex'
dim = 50
direction = 1
encoding = 'utf-8'

def on_connect(client, userdata, flags, rc):
  print('Connected with ESP32, result: ' + str(rc))
  client.subscribe(MQTT_TOPIC_BUTTON_SUB)
  client.subscribe(MQTT_TOPIC_FLEX_SUB)

def on_message(client, userdata, msg):
  global dim
  global direction
  if dim == 100:
      direction = -1
  elif dim == 0:
      direction = 1
  dim = dim + direction * 10
  print('Message topic: ' + msg.topic + ', message payload: ' + str(msg.payload))
 
  if msg.topic == MQTT_TOPIC_BUTTON_SUB:
      if client.publish(MQTT_TOPIC_BUTTON_PUB, '1: Button pushed - From Broker'):
          print('Published button message to esp8266')
      else:
          print('Button message failed to be published to esp8266')
  elif msg.topic == MQTT_TOPIC_FLEX_SUB:
      message_string = str(msg.payload, encoding)
      tokens = message_string[message_string.index('=>') + 2:].rstrip().split(',')
      roll = float(tokens[4])
      ledDim = int(100 * (roll + 180) / 360)
      if client.publish(MQTT_TOPIC_FLEX_PUB, '0 '+ str(ledDim)):
        print('Published flex sensor message to esp8266')
      else:
        print('Flex sensor message failed to be published to esp8266')
#      angle = float(tokens[0])
#      if angle <= 20 or angle >= 150:
#          ledDim = int((angle + 50) / 5.2)
#          if client.publish(MQTT_TOPIC_FLEX_PUB, '0 '+ str(ledDim)):
#              print('Published flex sensor message to esp8266')
#          else:
#              print('Flex sensor message failed to be published to esp8266')
  else:
      print('Message cannot be recognized.')
 
  # To modify it for our project:
  # msg should contain all sensor information from the microcontroller on the glove
  # Extract the msg, process the data, and reorganize sensor data in this format (this is only a placeholder for now)
  # =>[float flex_1],[float flex_2],[float flex_3],[float flex_4],[float IMU_Quat],[float IMU_x],[float IMU_y],[float IMU_z]
  sensorMessageQueue = SensorMessageQueue()
  message = '=>111,222.22,333.333,444.4,55.5,6.6666,77.7777,8888'
  SensorMessageQueue().pushNewMessage(message)
  SmartGloveControlSystem().handle_queue()
   

def main():
  mqtt_client = mqtt.Client()
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
  mqtt_client.on_connect = on_connect
  mqtt_client.on_message = on_message

  mqtt_client.connect(MQTT_ADDRESS, 1883)
  mqtt_client.loop_forever()

if __name__ == '__main__':
  print('main function')
  main()
