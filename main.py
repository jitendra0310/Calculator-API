from flask import Flask, render_template, session, request, jsonify
from flask_socketio import SocketIO
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
socketio = SocketIO(app, manage_session=True)

def calcExpression(exp, sender):
    terms = exp.split(" ")
    opr = terms[1]
    x = int(terms[0])
    y = int(terms[2])
    res = 0
    try:
        if terms[1] == '+':
            res = x + y
        elif terms[1] == '-':
            res = x - y
        elif terms[1] == '*':
            res = x * y
        elif terms[1] == '/':
            res = x / y
        elif terms[1] == '**':
            res = x ** y
        elif terms[1] == '%':
            res = x % y
    except:
        return []
    
    return [str(x) + ' ' + opr + ' ' + str(y) + ' = ' + str(res), str(res)]

def addSession(calc, sender):
    tmp = []
    if not 'data' in session:
        tmp = []
    else:
        tmp = session['data']
    
    for item in tmp:
        if item['sender'] == sender:
            return;            
    tmp.append({
        'calc': calc,
        'sender': sender
    })
    session['data'] = tmp


@app.route('/')
def home():
    if not 'data' in session:
        session['data'] = []    
    return render_template('session.html')


@app.route('/store', methods = ['POST'])
def sessions():
    posted = request.get_json()
    if posted['add'] == True:
        addSession(posted['calc'], posted['sender'])
    data = session['data'][-10:]
    res = {
        'data': data,
        'Status code': 200
    }
    return jsonify(res)


@socketio.on('event')
def userCalculate(json, methods=['GET', 'POST']):
    #print('received my event: ' + str(json))
    result = calcExpression(json['exp'], json['sender'])
    if len(result) == 2:
        res = {
            'result': result,
            'sender': json['sender']
        }
        socketio.emit('response', res)


if __name__ == '__main__':
    socketio.run(app, debug=False)
