import serial
import sys

# Thanks Happzy's dpt-tools project.
def connect_to_diagnosis(ttyName):
    myserial = None
    try:
        ser = serial.Serial(ttyName, 115200, timeout=1)
        # ser.open()
        if not ser.is_open:
            raise BaseException
        myserial = ser
    except BaseException as e:
        print(ttyName, str(e))
    return myserial

def diagnosis_login(myserial, username, password):
    try:
        myserial.write(b'\n')  # poke
        resp = myserial.read(50)
        dbg_print(resp)
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
    except serial.SerialTimeoutException as e:
        err_print('Timeout: {}'.format(e))
    except BaseException as e:
        err_print(str(e))
        return False
    if b'# ' in resp:
        return True
    return False

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

    for line in lines:
        res = diagnosis_login(myserial, account, line)
        if res == True:
            print('\r\n\r\n')
            print('--------------------')
            print('Password is ', line)
            print('--------------------')
            break

if __name__ == '__main__':
    main()