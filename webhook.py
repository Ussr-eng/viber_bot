import requests
import json
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

auth_token = config['database']['main_token']
hook = 'https://chatapi.viber.com/pa/set_webhook'
headers = {'X-Viber-Auth-Token': auth_token}


sen = dict(url=config['database']['host'],
           event_types = ["delivered", "seen", "failed", "subscribed", "unsubscribed", "conversation_started" ]
           , send_name=True, send_photo=True)
# sen - это body запроса для отправки к backend серверов viber
#seen, delivered - можно убрать, но иногда маркетологи хотят знать,
#сколько и кто именно  принял и почитал ваших сообщений,  можете оставить)

r = requests.post(hook, json.dumps(sen), headers=headers)
# r - это пост запрос составленный по требованиям viber
print(r.json())
# в ответном print мы должны увидеть "status_message":"ok" - и это значит,
#  что вебхук установлен

sen = {
    "receiver":"1gwYmkDPCCv0MqiBwy+t2A==",
    "type":"rich_media",
    "min_api_version":7,
    "rich_media":{
       "Type":"rich_media",
       "ButtonsGroupColumns":6,
       "ButtonsGroupRows":7,
       "BgColor":"#FFFFFF",
       "Buttons":[
          {
             "Columns":6,
             "Rows":3,
             "ActionType":"open-url",
             "ActionBody":"https://www.google.com",
             "Image":"http://html-test:8080/myweb/guy/assets/imageRMsmall2.png"
          },
          {
             "Columns":6,
             "Rows":2,
             "Text":"<font color=#323232><b>Headphones with Microphone, On-ear Wired earphones</b></font><font color=#777777><br>Sound Intone </font><font color=#6fc133>$17.99</font>",
             "ActionType":"open-url",
             "ActionBody":"https://www.google.com",
             "TextSize":"medium",
             "TextVAlign":"middle",
             "TextHAlign":"left"
          },
          {
             "Columns":6,
             "Rows":1,
             "ActionType":"reply",
             "ActionBody":"https://www.google.com",
             "Text":"<font color=#ffffff>Buy</font>",
             "TextSize":"large",
             "TextVAlign":"middle",
             "TextHAlign":"middle",
             "Image":"https://s14.postimg.org/4mmt4rw1t/Button.png"
          },
          {
             "Columns":6,
             "Rows":1,
             "ActionType":"reply",
             "ActionBody":"https://www.google.com",
             "Text":"<font color=#8367db>MORE DETAILS</font>",
             "TextSize":"small",
             "TextVAlign":"middle",
             "TextHAlign":"middle"
          },
          {
             "Columns":6,
             "Rows":2,
             "Text":"<font color=#323232><b>Hanes Men's Humor Graphic T-Shirt</b></font><font color=#777777><br>Hanes</font><font color=#6fc133>$10.99</font>",
             "ActionType":"open-url",
             "ActionBody":"https://www.google.com",
             "TextSize":"medium",
             "TextVAlign":"middle",
             "TextHAlign":"left"
          },
       ]
    }
 }