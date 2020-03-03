import os
import sys
import random 
import time 
import threading
import re
import logging as log

import telebot 
from telebot import types 
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# constantes
TOKEN_FILENAME = 'token.txt'
QUEST_FILENAME = 'preguntas.txt'

token = ''
knownUsers = []  # todo: save these in a file, 
userStep = {}  # so they won't reset every time the bot restarts 

commands = {  # command description used in the "help" command 
    'start'       : 'Bienvenido al chatbot', 
    'help'        : 'Esta instrucción te informa sobre los comandos de este bot',
    'quiz'        : 'Empieza el test',
    'b1'          : 'Realizar test del bloque 1',
    'b2'          : 'Realizar test del bloque 2',
    'b3'          : 'Realizar test del bloque 3',
    'b4'          : 'Realizar test del bloque 4',
    'score'       : 'Se obtiene la puntuación',
    'answers'     : 'Se obtiene tu respuesta y la respuesta correcta.',
    'stop'        : 'Se para el test y te da un resumen de tu puntuación.',
    'wiki'        : 'Busca información en la wikipedia'
}

pregunta_enunciado = ''
answer_user = ''
correct_answer = ''
correctAnswers = []
wrongAnswers = []
contador = 0
cont = 0
score = []
bloque_elegido = ''

#CONFIG
chatswl = [
    '000000', 
]

log.basicConfig(level=log.INFO, format='%(asctime)s %(levelname)s %(message)s')

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

def get_bloque_elegido():
    return bloque_elegido

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

def get_token():
    global token
    if os.path.exists(TOKEN_FILENAME):
        with open(TOKEN_FILENAME, 'r') as f:
            token = f.read().strip()
            return token
    else:
        print('El fichero '+TOKEN_FILENAME+' no encontrado.')
        sys.exit()

def echo(messages):
    t = threading.Thread(target=listener, args=(messages))
    t.start()

def log_command(m):
    log.info('El comando {} ha recibido el dato del chat: {}'.format(m.text, str(m.chat)))

# only used for console output now 
def listener(messages): 
    """ 
    When new messages arrive TeleBot will call this function. 
    """ 
    for m in messages: 
        if m.content_type == 'text': 
            # print the sent message to the console 
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text) 

bot = telebot.TeleBot(get_token()) 
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
    log_command(m) 
    cid = m.chat.id 
    help_text = "Los siguientes comando están disponibles para este bot: \n" 
    for key in commands:  # generate help text out of the commands dictionary defined at the top 
        help_text += "/" + key + ": " 
        help_text += commands[key] + "\n" 
    bot.send_message(cid, help_text)  # send the generated help page

# handle the "/quiz" command 
@bot.message_handler(commands=['quiz']) 
def command_quiz(m):
    log_command(m)
    chatId  = m.chat.id 
    msg     = m.text
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
    
    with open(QUEST_FILENAME, 'r') as f: 
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

        texto = "* %s)* %s \n %s \n %s \n %s \n %s \n\n De *%s*" % (bloqueMio.upper(), enunciado, opcion_a, opcion_b, opcion_c, opcion_d, autor)
        set_enunciado(enunciado)
        set_correct_answer(resp_correcta)
        bot.send_message(chatId, texto, parse_mode= 'Markdown', reply_markup=gen_markup())
        bot.send_message(chatId, "Para saber la respuesta correcta puedes escribir el comando /answers.") 
        bot.send_message(chatId, "Para saber tu puntuación puedes escribir el comando /score.") 
        bot.send_message(chatId, "Para que el bot te haga otra pregunta puedes escribir el comando /quiz.")

# handle the "/b1" or "/b2" or "/b3" or  "/b4" or  command
@bot.message_handler(commands=['b1', 'b2', 'b3', 'b4'])
def command_bloque(m):
    # Parse command correctly (avoid content after @)
    global bloque_elegido
    regex = re.compile('\/\w*')
    command = regex.search(m.text).group(0)
    bloque_elegido = command.replace("/", "")
    log_command(m)
    command_quiz_bloque(m)

def command_quiz_bloque(m):
    log_command(m)
    global bloque_elegido
    chatId  = m.chat.id 
    filas = []
    autor = ''
    enunciado = ''
    opcion_a = ''
    opcion_b = ''
    opcion_c = ''
    opcion_d = ''
    resp_correcta = ''
    nombre_bloque = ''
    bloque = bloque_elegido
    if bloque:  
        if bloque == 'b1':  
            nombre_bloque = 'bloque 1'
        elif bloque == 'b2':  
            nombre_bloque = 'bloque 2'
        elif bloque == 'b3':  
            nombre_bloque = 'bloque 3'
        elif bloque == 'b4':  
            nombre_bloque = 'bloque 4'

    with open(QUEST_FILENAME, 'r') as f:  
        preguntas = f.read().strip().splitlines()[1:]
        if bloque:
            preguntas2 = []  
            for pregunta in preguntas:  
                if pregunta.split(';')[0].lower() == bloque:  
                    preguntas2.append(pregunta)
                    preguntas = preguntas2
                    random.shuffle(preguntas)
            i=0
            for question in preguntas:
                filas.append(preguntas[i].strip(';'))
                i += 1
            for fila in filas:
                autor = fila.split(';')[1]
                enunciado = fila.split(';')[2]
                opcion_a = fila.split(';')[3]
                opcion_b = fila.split(';')[4]
                opcion_c = fila.split(';')[5]
                opcion_d = fila.split(';')[6]  
                resp_correcta = fila.split(';')[7]
 
            texto = "* %s)* %s \n %s \n %s \n %s \n %s \n\n De *%s*" % (bloque.upper(), enunciado, opcion_a, opcion_b, opcion_c, opcion_d, autor)
            set_enunciado(enunciado)
            set_correct_answer(resp_correcta)
            bot.send_message(chatId, texto, parse_mode= 'Markdown', reply_markup=gen_markup())
            bot.send_message(chatId, "Para saber la respuesta correcta puedes escribir el comando /answers.")  
            bot.send_message(chatId, "Para saber tu puntuación puedes escribir el comando /score.")
            bot.send_message(chatId, "Para que el bot te haga otra pregunta del *"+nombre_bloque+"* puedes escribir el /"+bloque+".", parse_mode= 'Markdown') 


@bot.message_handler(commands=['answers'])
def command_answers(m):
    log_command(m)
    global answer_user
    resp = get_user_answer()
    set_user_answer(None)
    if resp != None and resp != '':
        bot.send_message(m.chat.id, "Tu respuesta ha sido la *"+resp+"*.\n *La respuesta correcta es: "+get_correct_answer() +"*", parse_mode= 'Markdown')
    else:
        bot.send_message(m.chat.id, "No has respondido a la pregunta.\nPara empezar hacer el test puedes escribir el comando /quiz y después hacer clic en alguna de las opciones correspondientes.")

# handle the "/score" command 
@bot.message_handler(commands=['score']) 
def command_score(m): 
    log_command(m) 
    global score
    global answer_user
    answer_user = ''
    if score:
        bot.send_message(m.chat.id, "Respuestas *correctas*: "+str(score[0])+".\nRespuestas *incorrectas*: "+str(score[1])+".", parse_mode= 'Markdown')
        bot.send_message(m.chat.id, "Para parar el test puedes escribir el comando /stop.")
    else:
        bot.send_message(m.chat.id, "No hay puntuación, ya que no has respondido al test.\nPara empezar hacer el test puedes escribir el comando /quiz y después hacer clic en alguna de las opciones correspondientes.")

# handle the "/score" command 
@bot.message_handler(commands=['stop']) 
def command_stop(m):
    log_command(m)
    global correctAnswers
    global wrongAnswers
    global score
    global contador
    score = get_score()
    if score:
        bot.send_message(m.chat.id, "De las *"+str(contador)+"* preguntas.\nRespuestas *correctas* : "+str(score[0])+".\nRespuestas *incorrectas*: "+str(score[1])+".", parse_mode= 'Markdown')
        contador = 0
        correctAnswers = []
        wrongAnswers = []
        score = []
        set_user_answer(None)
        bot.send_message(m.chat.id, "Para empezar hacer el test puedes escribir el comando /quiz.")
        bot.send_message(m.chat.id, "Para realizar el test de algún puedes escribir el comando /b1 o /b2 o /b3 o /b4.")
    else:
        bot.send_message(m.chat.id, "No hay puntuación, ya que no has respondido al test.\nPara empezar hacer el test puedes escribir el comando /quiz y después hacer clic en alguna de las opciones correspondientes.")

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
    global contador
    global answer_user
    resp = call.data
    if resp != None:
        contador += 1
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
    else:
        answer_user = ''
        bot.answer_callback_query(call.id, None)

# handle the "/wiki" command
# filter on a specific message
@bot.message_handler(commands=['wiki'])
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_wiki(m):
    log_command(m)
    msg     = m.text
    repy = ''
    params = msg.split(' ')[1:]
    if params:
        lang = 'es'
        paramlang = params[0].lower().split(':')[0]
        search = '_'.join(params)
        search = search.lstrip('%s:' % paramlang)
        if paramlang in ['en', 'fr', 'de', 'pt']:
            lang = paramlang
        reply = "https://%s.wikipedia.org/wiki/%s" % (lang, search)
        bot.send_message(m.chat.id, reply, parse_mode='HTML')
        #bot.replay_to(reply, parse_mode='HTML')

# default handler for every other text 
@bot.message_handler(func=lambda message: True, content_types=['text']) 
def command_default(m): 
    # this is the standard reply to a normal message 
    bot.send_message(m.chat.id, "No te entiendo \"" + m.text + "\"\nPuedes escribir el comando /help para saber qué comando utilizar") 

print("El bot se esta ejecutando") 
bot.polling() 
