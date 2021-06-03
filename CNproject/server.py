'''if you enter the buzzer or the answer without pressing any key the code may get stuck into an infinite loop
and trying to run the server code may not work since the port will be busy and will take time so that you can
run the code again also run the server code first'''

import socket
import sys
import time
import select
import random

#Constants
connection_id = 0
connection_list = []
addresses = []
connections = {}
scores = {}
questions = list(range(0,20))
answers = list(range(0,20))

''' questions asked in the quiz are numbers from 0 to 20 and the answer to them is the number itself'''

instructions = "Hello and welcome to the show KBC.\nI am your host Amitabh Bachchan.\n\n\
Today 3 of you will be competiting in the show.\n\
There will be 20 questions, the one who answer's 5 questions correctly wins the show\n\n\
You can press any button as buzzer and one who presses first \
will have 60s to answer question .\n\n\n"


def create_socket():
    '''Function to create Socket'''
    try:
        global host
        global port
        global s
        host = ""
        port = 3333
        s = socket.socket()
    except socket.error as err:
        print("Port not available :",err)

def bind_socket():
    try:
        global host
        global port
        global s
        s.bind((host,port))
        print("Binding the Port ...")
        s.listen(5)
    except socket.error as err:
        print("Not possible to bind the socket :",err)


def accepting_connections():
    '''Function To accept all connections that are initiated from client side. Gives a identification no. the client.'''
    for conn in connections:
        connections[conn].close()
    count = 1
    global connection_id
    print("Game will start when all 3 players have joined")
    while(len(connections)<3):
            conn,address = s.accept()
            s.setblocking(1)#Prevents timeout of connections
            scores[connection_id] = 0
            connections[connection_id] = conn
            addresses.append(address)
            conn.send(str.encode(str(connection_id)))
            connection_id += 1
            print("Player",count,"has joined the Game",address[0])
            count += 1
    for conn in connections:
        connection_list.append(connections[conn])
        connections[conn].send(str.encode(instructions))
    Game()

def Game():
    '''Main Game '''
    global quesno 
    quesno = getQuestion()
    while True:
        try:
            running = True
            while running:
                print("Sending")
                send_question(quesno)
                questions.remove(questions[quesno])
                buzzer_recv = select.select(connection_list,[],[],15)
                print(buzzer_recv)
                if(len(buzzer_recv[0])>0):
                    print("Buzzer received")
                    buzzer_data = buzzer_recv[0][0].recv(1024)
                    buzzer_data = buzzer_data.decode("utf-8")
                    connection_id,buzzer_data = buzzer_data.split()
                    print(connection_id, buzzer_data)
                    send_buzzer_information(connection_id)
                    get_answer(connection_id)
                else:
                    send_buzzer_information(-1)
                if(len(questions)==0):
                    GameOver()
                    sys.exit()
                check_max_score()
                answers.remove(answers[quesno])
                quesno = getQuestion()

        except Exception as e:
            print("Error occurred in handling connection :",e)
            accepting_connections()

def getQuestion():
    r = random.randrange(0,len(questions))
    ques = questions[r]
    return r

def send_question(quesno):
    '''to broadcast question to all  clients'''
    time.sleep(1)
    for conn in connections:
        connections[conn].send(str.encode(str(questions[quesno])))

def send_buzzer_information(id):
    '''Sends buzzer information to the clients regarding Who has pressed it or is it pressed?'''
    msg = "Player "+str(id)+" has pressed the buzzer"
    if id ==-1:
        msg = "No One has Pressed the buzzer. Next Question will be prompted now\n"
    print(msg)
    for conn in connections:
        if str(conn) != str(id):
            connections[conn].send(str.encode(msg))

def get_answer(id):
    '''Prompts clients which player has pressed the buzzer '''
    connections[(int)(id)].send("Your Answer:".encode("utf-8"))
    answer = connections[(int)(id)].recv(1024)
    answer = answer.decode("utf-8")
    print(answer)
    result = check_answer(answer)
    if result:
        send_answer_info(id,True)
        scores[(int)(id)] = scores[(int)(id)] + 1
        print(scores)
    else:
        send_answer_info(id,False)

def check_answer(answer):
    '''verify answer'''
    if str(answer) == str(answers[quesno]):
        return True
    else:
        return False

def send_answer_info(id,correct):
    '''tell the client, whether the person who pressed the buzzer gave the right or wrong answer'''
    msg = ''
    if correct:
        msg = "Player "+str(id)+" has given the right answer"
    else:
        msg = "Player "+str(id)+" has given the wrong answer" 
    for conn in connections:
        if str(conn) != str(id):
            connections[conn].send(msg.encode("utf-8"))
        elif correct:
            connections[conn].send("Right Answer".encode("utf-8"))
        else:
            connections[conn].send("Wrong Answer".encode("utf-8"))

def check_max_score():
    '''If Score is 5, game is terminated'''
    winid = max(scores,key = scores.get)
    if scores[winid] == 5:
        GameOver()
        sys.exit()

def GameOver():
    '''Loop to terminate the Game and notifys the client.'''
    global scores
    winid = max(scores,key = scores.get)
    quit = "quit"
    for conn in connections:
        connections[conn].send(quit.encode("utf-8"))

    msg = "Player "+str(winid)+" has won the game\n"+"Final Scores are:"

    for conn in connections:
        if str(conn)  == str(winid):
            st = "Congratulations!!! You won the Game with score:"+str(scores[winid])
            connections[conn].send(st.encode("utf-8"))
        else:
            connections[conn].send(msg.encode("utf-8"))

    for conn in connections:
        print("sending to ",conn)
        for s in sorted(scores):
            time.sleep(1)
            st = "Player "+str(s)+":"+str(scores[s])
            connections[conn].send(str.encode(st))
    
    for conn in connections:
        connections[conn].send("GameOver Goodbye".encode("utf-8"))
    time.sleep(5)

def Main():
    create_socket()
    bind_socket()
    accepting_connections()
if __name__=='__main__':
	Main()
