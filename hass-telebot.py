#!/srv/telebot/bin/python3.5
import time
import random
import datetime
import telepot
import argparse
from configobj import ConfigObj
import homeassistant.remote as remote

# Get command line args
parser = argparse.ArgumentParser()

parser.add_argument("config", help="full path to config file", type=str)
args = parser.parse_args()
config_file = args.config

# Read Config File
config = ConfigObj(config_file, file_error=True)

ha_url = config['ha_url']
ha_key = config['ha_key']
ha_port = config['ha_port']
ha_ssl = config['ha_ssl']
ha_alarm_code = config['ha_alarm_code']
bot_token = config['bot_token']
allowed_chat_id = config['allowed_chat_id']

api = remote.API(ha_url, ha_key, ha_port, ha_ssl)
print(remote.validate_api(api))

print('-- Available services:')
services = remote.get_services(api)
for service in services:
    print(service['services'])

bot = telepot.Bot(bot_token)

# Devices to load info from
devices = ['alarm_control_panel.ha_alarm']

def get_state (entity_id):
  entity = remote.get_state(api, entity_id)
  state = format('{} is {}.'.format(entity.attributes['friendly_name'], entity.state))

  print(state)
  return state

def service_call (domain, service, payload):
  remote.call_service(api, domain, service, payload)

def handle(msg):

    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if (content_type == 'text') and (chat_id == int(allowed_chat_id)):
      command = msg['text']

      print(command)

      if command == '/roll':
          bot.sendMessage(chat_id, random.randint(1,6))
      elif command == '/time':
          bot.sendMessage(chat_id, str(datetime.datetime.now()))
      elif command == '/start':
          bot.sendMessage(chat_id, 'hola!')
      elif command == '/states':
          for s in devices:
            state = get_state(s)
            bot.sendMessage(chat_id, state)
      elif command == '/armhome':
          payload = {'code': ha_alarm_code}
          service_call('alarm_control_panel','alarm_arm_home',payload)
          bot.sendMessage(chat_id, 'Home alarm mode should be pending')
      elif command == '/armaway':
          payload = {'code': ha_alarm_code}
          service_call('alarm_control_panel','alarm_arm_away',payload)
          bot.sendMessage(chat_id, 'Away alarm mode should be pending')
      elif command == '/disarm':
          payload = {'code': ha_alarm_code}
          service_call('alarm_control_panel','alarm_disarm',payload)
          bot.sendMessage(chat_id, 'You are welcome!')
      elif command == '/alarm':
          replymarkup = {
            "keyboard": [[{"text":"/disarm"}], [{"text":"/armhome"}], [{"text":"/armaway"}]],
            "resize_keyboard": True,
            "one_time_keyboard": True
          }
          bot.sendMessage(chat_id, 'Please choose an alarm option...',reply_markup=replymarkup)
      elif command == '/menu':
          replymarkup = {
            "keyboard": [[{"text":"/alarm"}], [{"text":"/states"}], [{"text":"/roll"}]],
            "resize_keyboard": True,
            "one_time_keyboard": True
          }
          bot.sendMessage(chat_id, 'Please choose an option...',reply_markup=replymarkup)
    else:
        bot.sendMessage(chat_id, 'You are not authorised to chat with me!')

bot.message_loop(handle)
print('I am listening ...')

while 1:
    time.sleep(10)
