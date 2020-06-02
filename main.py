import serial
import sys

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

        # previous result in this reading(not usually).
        if b'# ' in resp:
            return 2

        if b'login' in resp:
            dbg_print('Entering username {}'.format(username))
            myserial.write(username.encode() + b'\n')
            resp = myserial.read(50)
            dbg_print(resp)
            if b'Password' in resp:
                dbg_print('Entering password {}'.format(password))
                myserial.write(password.encode() + b'\n')
                resp = myserial.read(80)
                dbg_print(resp)

                if b'# ' in resp:
                    return 2
                elif b'login' in resp:
                    return 1
                else:
                    # result is not back, read again.
                    # but second reading enters "login phase", the next password will try to login twice.
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
    print("[debug] {}".format(content))

def main():
    # linux is /dev/ttyACMX
    com_port = 'COM4'

    account = 'root'
    password_file = 'xato-net-10-million-passwords.txt'

    myserial = connect_to_diagnosis(com_port)

    if myserial == None:
        sys.exit()

    f = open(password_file, 'r')
    lines = f.readlines()
    f.close()

    i = 1
    for line in lines:
        # remove \r\n
        line = line.replace('\r', '')
        line = line.replace('\n', '')

        print('-------------------------------------')
        print(i, line)
        i = i + 1

        res = 0
        while res == 0:
            res = diagnosis_login(myserial, account, line)

        if res == 2:
            print('\r\n\r\n')
            print('--------------------')
            print('Password is ', line)
            print('--------------------')
            break

if __name__ == '__main__':
    main()
