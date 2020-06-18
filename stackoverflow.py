import serial

import os
import sys

logger = None

# Thanks Happzy's dpt-tools project.
def connect_to_diagnosis(ttyName):
    myserial = None
    try:
        ser = serial.Serial(ttyName, 115200, timeout=2)
        # ser.open()
        if not ser.is_open:
            raise BaseException
        myserial = ser
    except BaseException as e:
        print(ttyName, str(e))
    return myserial

# 0 - com port issue, retry.
# 1 - password is wrong.
# 2 - password is right.
def diagnosis_login(myserial, username, password):
    try:
        myserial.write(b'\n')  # poke
        resp = myserial.read(50)
        dbg_print(resp)

        # The previous result is in this reading(not usually).
        if b'# ' in resp:
            return 2

        if b'login' in resp:
            dbg_print('Entering username {}'.format(username))
            myserial.write(username.encode() + b'\n')
            resp = myserial.read(50)
            dbg_print(resp)
            if b'Password' in resp:
                #dbg_print('Entering password {}'.format(password))
                myserial.write(password + b'\n')
                resp = myserial.read(80)
                dbg_print(resp)

                if b'incorrect' in resp:
                    return 1
                elif b'# ' in resp:
                    return 2
                else:
                    # The result is not back, read again.
                    # But second reading enters "login phase", the next password will try to login twice.
                    resp = myserial.read(80)
                    dbg_print(resp)
            else:
                return 0
        else:
            return 0

    except serial.SerialTimeoutException as e:
        err_print('Timeout: {}'.format(e))
        return 0
    except BaseException as e:
        err_print(str(e))
        return 0
    if b'# ' in resp:
        return 2
    return 1

def err_print(content):
    print("[error] {}".format(content))

def dbg_print(content):
    s = "[debug] {}".format(content)
    print(s)

    global logger
    logger.write(s)

def main():
    # linux is /dev/ttyACMX
    com_port = 'COM4'

    account = 'root'

    myserial = connect_to_diagnosis(com_port)

    if myserial == None:
        sys.exit()

    global logger
    logger = open('Log.txt', 'a')

    one = [0xFF];

    for i in range(1662, 10000, 1):
        line = bytes(one * (i+1))

        print('-------------------------------------')
        #print(i, line)
        print(i)
        
        res = 0
        while res == 0:
            res = diagnosis_login(myserial, account, line)

        logger.flush()

        if res == 2:
            print('\r\n\r\n')
            print('--------------------')
            print('Password is ', line)
            print('--------------------')
            break

        # ecsape
        if os.path.isfile('QUIT'):
            break

    logger.write('-------------------------------------\n\n')
    logger.close()

    myserial.close()

if __name__ == '__main__':
    main()
