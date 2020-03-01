import os
import sys
import random 
import time 
import threading

import telebot 
from telebot import types 
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

token = '' 
knownUsers = []  # todo: save these in a file, 
userStep = {}  # so they won't reset every time the bot restarts 

commands = {  # command description used in the "help" command 
    'start'       : 'Bienvenido al chatbot', 
    'help'        : 'Esta instrucción te informa sobre los comandos de este bot',
    'quiz'        : 'Empieza el test' ,
    'score'       : 'Se obtiene la puntuación',
    'answers'     : 'Se obtiene tu respuesta y la respuesta correcta.',
    'stop'        : 'Se para el test y te da un resumen de tu puntuación.'
}

pregunta_enunciado = ''
answer_user = ''
correct_answer = ''
correctAnswers = []
wrongAnswers = []
contador = 0
cont = 0
score = []

#CONFIG
chatswl = [
    '000000', 
]

# error handling if user isn't known yet 
# (obsolete once known users are saved to file, because all users 
#   had to use the /start command and are therefore known to the bot) 
def get_user_step(uid): 
    if uid in userStep: 
        return userStep[uid] 
    else: 
        knownUsers.append(uid) 
        userStep[uid] = 0 
        print("Nuevo usuario detectado que todavía no ha utilizado el comando \"/start\" .") 
        return 0

def set_user_answer(user_answer):
    global answer_user    
    if user_answer != None:
        answer_user = user_answer

def get_user_answer():
    return answer_user

def set_correct_answer(correct):
    global correct_answer    
    if correct != None:
        correct_answer = correct

def get_correct_answer():
    return correct_answer

def set_enunciado(enunciado):
    global pregunta_enunciado    
    if enunciado != None:
        pregunta_enunciado = enunciado

def get_enunciado():
    return pregunta_enunciado

def get_score():
    return score

def get_puntuacion():
    global correctAnswers
    global wrongAnswers
    global score
    global cont
    cont += 1
    if get_user_answer() == get_correct_answer():
        correctAnswers.append(get_enunciado())
    else:
        wrongAnswers.append(get_enunciado())
    if cont == 1:
        score.append(len(correctAnswers))
        score.append(len(wrongAnswers))
    elif cont > 1:
        score.insert(0, len(correctAnswers))
        score.insert(1, len(wrongAnswers))
    return score

def echo(messages):
    t = threading.Thread(target=listener, args=(messages))
    t.start()

# only used for console output now 
def listener(messages): 
    """ 
    When new messages arrive TeleBot will call this function. 
    """ 
    for m in messages: 
        if m.content_type == 'text': 
            # print the sent message to the console 
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text) 

filename = 'token.txt'
if os.path.exists(filename):
    with open(filename, 'r') as f:
            token = f.read().strip()
else:
    print(filename+' not found.')
    sys.exit()
bot = telebot.TeleBot(token) 
bot.set_update_listener(listener)  # register listener 

# handle the "/start" command 
@bot.message_handler(commands=['start']) 
def command_start(m): 
    cid = m.chat.id 
    if cid not in knownUsers:  # if user hasn't used the "/start" command yet: 
        knownUsers.append(cid)  # save user id, so you could brodcast messages to all users of this bot later 
        userStep[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" command 
        bot.send_message(cid, "Bienvenido.") 
        bot.send_message(cid, "Ahora te conoczco.") 
        command_help(m)  # show the new user the help page 
    else: 
        bot.send_message(cid, "Ya te conozco") 


# help page 
@bot.message_handler(commands=['help']) 
def command_help(m): 
    cid = m.chat.id 
    help_text = "Los siguientes comando están disponibles para este bot: \n" 
    for key in commands:  # generate help text out of the commands dictionary defined at the top 
        help_text += "/" + key + ": " 
        help_text += commands[key] + "\n" 
    bot.send_message(cid, help_text)  # send the generated help page

# handle the "/quiz" command 
@bot.message_handler(commands=['quiz']) 
def command_quiz(m):
    chatId  = m.chat.id 
    msg     = m.text 
    global contador
    contador += 1
    reply = '' 
    params = msg.split(' ')[1:] 
    bloque = '' 
    filas = []
    bloqueMio = ''
    autor = ''
    enunciado = ''
    opcion_a = ''
    opcion_b = ''
    opcion_c = ''
    opcion_d = ''
    resp_correcta = ''
    if params: 
        if params[0].lower() == 'b1': 
            bloque = 'b1' 
        elif params[0].lower() == 'b2': 
            bloque = 'b2' 
        elif params[0].lower() == 'b3': 
            bloque = 'b3' 
        elif params[0].lower() == 'b4': 
            bloque = 'b4' 
    
    with open('preguntas.txt', 'r') as f: 
        preguntas = f.read().strip().splitlines()[1:]
        if bloque: 
            preguntas2 = [] 
            for pregunta in preguntas: 
                if pregunta.split(';')[0].lower() == bloque.lower(): 
                    preguntas2.append(pregunta)
            preguntas = preguntas2
        random.shuffle(preguntas)
        i=0
        for question in preguntas:
            filas.append(preguntas[i].strip(';'))
            i += 1
        for fila in filas:
            bloqueMio = fila.split(';')[0]
            autor = fila.split(';')[1]
            enunciado = fila.split(';')[2]
            opcion_a = fila.split(';')[3]
            opcion_b = fila.split(';')[4]
            opcion_c = fila.split(';')[5]
            opcion_d = fila.split(';')[6]       
            resp_correcta = fila.split(';')[7]    
        texto = "* %s)* %s \n %s \n %s \n %s \n %s" % (bloqueMio.upper(), enunciado, opcion_a, opcion_b, opcion_c, opcion_d)
        set_enunciado(enunciado)
        set_correct_answer(resp_correcta)
        bot.send_message(chatId, texto, parse_mode= 'Markdown', reply_markup=gen_markup())
        bot.send_message(chatId, "Para saber la respuesta correcta puedes escribir el comando /answers.") 
        bot.send_message(chatId, "Para saber tu puntuación puedes escribir el comando /score.") 
        bot.send_message(chatId, "Para que el bot te haga otra pregunta puedes escribir el comando /quiz.") 

@bot.message_handler(commands=['answers'])
def command_answers(m):
    bot.send_message(m.chat.id, "Tu respuesta ha sido la *"+get_user_answer()+"*.\n *La respuesta correcta es: "+get_correct_answer() +"*", parse_mode= 'Markdown')

# handle the "/score" command 
@bot.message_handler(commands=['score']) 
def command_score(m):  
    global score
    bot.send_message(m.chat.id, "Respuestas *correctas*: "+str(score[0])+".\nRespuestas *incorrectas*: "+str(score[1])+".", parse_mode= 'Markdown')
    bot.send_message(m.chat.id, "Para empezar hacer el test puedes escribir el comando /quiz.")

# handle the "/score" command 
@bot.message_handler(commands=['stop']) 
def command_stop(m):
    global correctAnswers
    global wrongAnswers
    global score
    global contador
    score = get_score()
    bot.send_message(m.chat.id, "De las *"+str(contador)+"* preguntas.\nRespuestas *correctas* : "+str(score[0])+".\nRespuestas *incorrectas*: "+str(score[1])+".", parse_mode= 'Markdown')
    contador = 0
    correctAnswers = []
    wrongAnswers = []
    score = []

def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 4
    markup.add(InlineKeyboardButton("a", callback_data="a"),
               InlineKeyboardButton("b", callback_data="b"),
               InlineKeyboardButton("c", callback_data="c"),
               InlineKeyboardButton("d", callback_data="d"))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    set_user_answer(call.data)
    get_puntuacion()
    if call.data == "a":
        bot.answer_callback_query(call.id, "a")
    elif call.data == "b":
        bot.answer_callback_query(call.id, "b")
    elif call.data == "c":
        bot.answer_callback_query(call.id, "c")
    elif call.data == "d":
        bot.answer_callback_query(call.id, "d")


# default handler for every other text 
@bot.message_handler(func=lambda message: True, content_types=['text']) 
def command_default(m): 
    # this is the standard reply to a normal message 
    bot.send_message(m.chat.id, "No te entiendo \"" + m.text + "\"\nPuedes escribir el comando /help para saber qué comando utilizar") 

print("El bot se esta ejecutando") 
bot.polling() 
