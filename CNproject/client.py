'''if you enter the buzzer or the answer without pressing any key the code may get stuck into an infinite loop
and trying to run the server code may not work since the port will be busy and will take time so that you can
run the code again also run the server first'''

''' questions asked in the quiz are numbers from 0 to 20 and the answer to them is the number itself'''

import socket
import os
import select
import time
import sys

#Constants
TIMEOUT = 11

s = socket.socket()
host = "127.0.0.1"
port = 3333

s = socket.socket()
s.connect((host,port))
conn_id = s.recv(1024)
conn_id = conn_id.decode("utf-8")
instructions = s.recv(1024)
print(instructions.decode("utf-8"))
message = "NOANSWER"
time.sleep(5)

def GameOver():
    '''Game over loop'''
    msg = s.recv(1024)
    print(msg.decode("utf-8"))
    s1 = s.recv(1024)
    s2 = s.recv(1024)
    s3 = s.recv(1024)
    print(s1.decode("utf-8"))
    print(s2.decode("utf-8"))
    print(s3.decode("utf-8"))
    t = s.recv(1024)
    print(t.decode("utf-8"))
    sys.exit()
    
def Main():
    '''Game Controller (Client Side)'''
    while True:
        print('\n')
        data = s.recv(1024)
        response = data.decode("utf-8")
        if(response == 'quit'):
            GameOver()
        elif(len(data)>0):
            print("Question :",response)

        lst = select.select([sys.stdin,s],[],[],10)
        if(len(lst[0])>0) and (lst[0][0]==sys.stdin):
            buzzer = input()
            buzzer = conn_id + " " + buzzer 
            s.sendall(buzzer.encode("utf-8"))
            print("Buzzer pressed",buzzer)
        elif (len(lst[0])>0) and (lst[0][0]==s):
            buzzer_info = s.recv(1024)
            buzzer_info = buzzer_info.decode("utf-8")
            print(buzzer_info)
            ans = s.recv(1024)
            ans = ans.decode("utf-8")
            print(ans)
            continue
        else:
            print("TIME's UP.")
        buzzer_info = s.recv(1024)
        buzzer_info = buzzer_info.decode("utf-8")
        if(buzzer_info == 'Your Answer:'):
            print("You have 60s to answer the question.\n"+buzzer_info)
            anslst = select.select([sys.stdin],[],[],60)
            if(len(anslst[0])>0):
                answer = input()
                s.sendall(answer.encode("utf-8"))
                ans = s.recv(1024)
                ans = ans.decode("utf-8")
                print(ans)
            else:
                print("Time's Up!!")
                s.sendall(message.encode("utf-8"))
                ans = s.recv(1024)
                ans = ans.decode("utf-8")
                print(ans)
                
    s.close()

if __name__ == '__main__':
    Main()
