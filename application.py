import os, time
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
#from werkzeug import secure_filename

app = Flask(__name__)


app.config["SECRET_KEY"] = 'SECRET!'
app.config['DEBUG'] = False
#app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config['UPLOAD_FOLDER'] = 'uploads/'
socket = SocketIO(app,engineio_logger=True,log_output=False,async_mode='eventlet')
#socket = SocketIO(app,async_mode='eventlet')
#socket = SocketIO(app)

channels = ['School','University','Friends','Office']
users = {}
messages ={
    'School':[
        {'user':'Riya','msg':'hello1 School','time':'123'},
        {'user':'Diya','msg':'hello2 School','time':'1234'}
        ],
    'University':[
        {'user':'Riya','msg':'hello1 university','time':'123'},
        {'user':'Diya','msg':'hello2 university','time':'1234'}
    ],
    'Friends':[
        {'user':'Diya','msg':'hello1 Friends','time':'123'}
    ],
    'Office':[
        {'user':'Harish','msg':'hello1 Office','time':'123'}
    ]
}


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['POST','GET'])
def login():

    if request.method == 'POST':
        username = request.form.get('username').capitalize()
        channel = 'School'
    else:
        username = request.args.get('username')
        channel = request.args.get('channel')

    if username not in users:
        users[username] = 'sid'

    return loadpage(username,channel,text1='Loggedin Successfully')


@app.route('/createchannel', methods=['POST'])
def createchannel():
    newchannel = request.form.get('newchannel')
    username = request.form.get('username')
    if newchannel in channels:
        text1 = "Channel already exists"
    else:
        channels.append(newchannel)
        messages[newchannel] = []
        text1 = "Channel Added Successfully"
    return loadpage(username,newchannel,text1)


def loadpage(username,channel,text1=''):
    return render_template('index.html',channels=channels,channel=channel,user=username,text1=text1)

@app.route('/getmsg/<string:channel>',methods=['GET'])
def getmsg(channel):
    try:
        msgs = messages[channel]
    except KeyError:
        pass
    return jsonify({'msgs':msgs})

@app.route('/uploader',methods=['POST'])
def uploader():
    f = request.files['file']
    f.save(os.path.join('uploads/',f.filename))
    #f.save(secure_filename(f.filename))
    user = request.form.get('user')
    channel = request.form.get('channel')
    filePath = 'uploads/' + f.filename
    filelink = filePath + f.filename
    #filelink = f"<a href='{filePath}'>{f.filename}</a>"
    msg = {'user':user,'msg':filelink,'time':time.ctime()}
    messages[channel].append(msg)
    text1 = 'File Uploaded Succesfully'
    return loadpage(user,channel,text1)

@app.route('/about')
def about():
    return render_template('about.html')

@socket.on('register sid')
def registersid(data):
    users[data['username']] = request.sid
    emit('announce connected',data,broadcast=True)

@socket.on('disconnect')
def deregistersid():
    sid = request.sid
    a1 = [user for user,s in users.items() if s == sid]
    try:
        a1 = a1[0]
    except IndexError:
        pass
    emit('announce disconnected',{'user':a1},broadcast=True)

@socket.on('submit msg')
def submitmsg(data):
    user = data['user']
    msg = data['msg']
    curTime = time.ctime()
    currMsg = {'user':user,'msg':msg,'time':curTime}
    msglen = len(messages[data['channel']])
    if msglen >= 100:
        messages[data['channel']].pop(0) 
    messages[data['channel']].append(currMsg)
    data['time'] = curTime
    emit('submit done',data,broadcast=True)

@socket.on('del-msg')
def delmsg(data):
    msgs = messages[data['channel']]
    for i in range(len(msgs)):
        if msgs[i]['user'] == data['username'] and msgs[i]['msg'] == data['msg'] and msgs[i]['time'] == data['time']:
            msgToDelete = msgs[i]
            messages[data['channel']].pop(i)
            msgToDelete['channel'] = data['channel']
            print('Message Deleted ',msgToDelete)
            emit('del-msg done',msgToDelete,broadcast=True)
            break

@socket.on('pvt msg')
def pvtmsg(data):
    toUser = data['toUser'].strip()
    try:
        tosid = users[toUser]
    except KeyError:
        mySid = users[data['fromUser']]
        emit('pvt msg offline',data,room=mySid)
    emit('pvt msg done',data,room=tosid)


if __name__ == "__main__":
    socket.run(app,host="0.0.0.0",port=int(os.environ["PORT"].rstrip()))
    #socket.run(app,debug=False)