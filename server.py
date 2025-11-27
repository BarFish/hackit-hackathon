from flask import Flask
from time import sleep

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
@app.route('/<string:inPass>', methods=['GET','POST'])
def index(inPass=''):
    res = verifyPassword(inPass)
    if res==True:
        return '1'
    else:
        return '0'


SECRET_PASSWORD = '1234'
Delay=0.15
longPadding  = ' '*12


def verifyPassword(inPass):
    result = True
    #pad secret password and input password to same length
    paddingInPassword = (longPadding + inPass)[-len(longPadding):]
    paddedSecretPassword = (longPadding + SECRET_PASSWORD)[-len(longPadding):]
    i = 0
    for ch in paddedSecretPassword:
        if paddingInPassword[i] != ch:
            sleep(Delay)
            result = False
        i = i + 1
    return result


if __name__== "__main__":
    app.run(debug=True)
