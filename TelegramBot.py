import settings
import csv
import openai
import telebot
import re

openai.api_key= settings.OPENAI_API_KEY
bot = telebot.TeleBot(settings.BOT_API_KEY)
  
# Using /shutdown command
@bot.message_handler(commands=['shut'])
def shutdown(message):
  OWNER_ID =6193803846
  if message.from_user.id == OWNER_ID: 
    exit()


models = {
    'gpt3.5': 'gpt-3.5-turbo',
    'dav3': 'text-davinci-003'
}

current_model = 'gpt3.5'

@bot.message_handler(commands=['mode','Mode'])
def change_model(message):
  try:
    global current_model
    new_model = message.text.split()[1]
    if new_model in models:
        current_model = new_model
        bot.send_message(message.chat.id, f"Model switched to {current_model}")
    else:
        bot.send_message(message.chat.id, "Invalid model name. Please enter a valid model name.")
  except:
    bot.send_message(message.chat.id, "Something went wrong. Please make sure you enter a valid command and a number dav3 or gpt3.5")

temp = 0.7
@bot.message_handler(commands=['temp'])
def change_temp(message):
  try:
    new_temp = message.text.split()[1]
    if 0 <= float(new_temp) <= 1:
      global temp
      temp = float(new_temp)
      bot.send_message(message.chat.id, f"Temperature changed to {temp}")
    else:
      bot.send_message(message.chat.id, "Invalid temperature value. Please enter a number between 0 and 1.")
  except:
    bot.send_message(message.chat.id, "Something went wrong. Please make sure you enter a valid command and a number between 0 and 1.")


@bot.message_handler(commands=['help'])
def help(message):
  bot.send_message(message.chat.id, f"""This bot has two models. Currently using the {current_model} model.
  
  dav3 is a weaker language model. She also doesn't remember dialogue. gpt3.5 is the model currently used in ChatGPT. Also, this model remembers the dialogue, which makes it an indispensable assistant.
  
  To change the model type /model followed by gpt3.5 or dav3
  
  For dev3, there is a temperature setting (/temp) from 0 to 1. The higher the temperature, the less formal text the model produces. If the value is high, there may be factual errors!""")

  
    


messages = [{"role": "system", "content": "You are a helpful assistant."},]

@bot.message_handler(func=lambda _:True)
def handle_message(message):
  if current_model == 'gpt3.5':
    message_dict = {"role": "user", "content": message.text }
    messages.append(message_dict)
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo", 
      messages=messages
    )
    reply = response.choices[0].message.content #response['choices'][0]['text']
    bot.send_message(chat_id=message.from_user.id,text=reply)
    messages.append({"role": "assistant", "content": reply})
  elif current_model == 'dav3':
    response = openai.Completion.create(
    model="text-davinci-003",
    prompt=message.text, 
    temperature=temp,       
    max_tokens=1000,       
    top_p=1,                
    frequency_penalty=0.0,  
    presence_penalty=0.6,   
    stop=[" Human:", " AI:"]
  )
    reply = response['choices'][0]['text']
    bot.send_message(chat_id=message.from_user.id,text=reply)

  with open("private/messages.csv", "a") as file:
    Response = re.sub(r"\n+", "", reply)
    writer = csv.writer(file)
    writer.writerow([message.text, Response])
    print(message.from_user.first_name + ': ' + message.text + '\n')
    print('TeleBotAI: '+Response+'\n')
    file.close()



bot.polling()


