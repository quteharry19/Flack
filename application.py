import os, time
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)
engine = create_engine('sqlite:///chats.db')
db = scoped_session(sessionmaker(bind=engine))

#app.config["SECRET_KEY"] = 'SECRET!'
app.config['DEBUG'] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config['UPLOAD_FOLDER'] = 'uploads/'
socket = SocketIO(app,engineio_logger=False,log_output=False,async_mode='eventlet')
#socket = SocketIO(app,async_mode='eventlet')
#socket = SocketIO(app)

channels = []
#channels = ['School','Friends','Office']
users = {}
# messages ={
#     'School':[
#         {'user':'Riya','msg':'hello1 School','time':'123'},
#         {'user':'Diya','msg':'hello2 School','time':'1234'}
#         ],
#     'Friends':[
#         {'user':'Diya','msg':'hello1 Friends','time':'123'}
#     ],
#     'Office':[
#         {'user':'Harish','msg':'hello1 Office','time':'123'}
#     ]
# }
messages = {}

@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['POST','GET'])
def login():

    global users

    if request.method == 'POST':
        username = request.form.get('username').capitalize()
        channel = 'School'
    else:
        username = request.args.get('username')
        channel = request.args.get('channel')

    users_query = db.execute("select username,sid from users").fetchall()
    users = {u1:s for u1,s in users_query }

    if username not in users:
        print('New user Logged',username)
        users[username] = ''
        id = get_max_id("users")
        db.execute("insert into users values (:id,:username,:sid)",{'id':id,'username':username,'sid':''})
        db.commit()

    channels = db.execute("select channel_name from channels").fetchall()
    channels = [chl[0] for chl in channels]

    if channel not in channels :
        id = get_max_id("channels")
        db.execute("insert into channels values (:id,:channel_name)",{'id':id,'channel_name':channel})
        db.commit()

    return loadpage(username,channel,text1='Loggedin Successfully')


def get_max_id(table_name):
    id = db.execute(f"select max(id) as id from {table_name}").fetchone()
    if id[0] is None:
        id = 1
    else :
        id = int(id[0])+1
    return id

@app.route('/createchannel', methods=['POST'])
def createchannel():
    newchannel = request.form.get('newchannel')
    username = request.form.get('username')
    if newchannel in channels:
        text1 = "Channel already exists"
    else:
        channels.append(newchannel)
        print('channels after append',channels)
        id = get_max_id("channels")
        db.execute("""insert into channels (id,channel_name) 
                    values (:id, :newchannel)""", {"id": id, 'newchannel': newchannel })
        db.commit()
        messages[newchannel] = []
        text1 = "Channel Added Successfully"
    return loadpage(username,newchannel,text1)


def loadpage(username,channel,text1=''):
    channel_list = db.execute("select channel_name from channels").fetchall()
    channels = [chl3 for chl2 in channel_list for chl3 in chl2]
    return render_template('index.html',channels=channels,channel=channel,user=username,text1=text1)

@app.route('/getmsg/<string:channel>',methods=['GET'])
def getmsg(channel):
    msgs = []
    try:
        channel_id = db.execute("select id from channels where channel_name = :channel_name", {'channel_name' : channel}).fetchone()
        channel_id = int(channel_id[0])

        msg1 = db.execute("""select (select username from users where id = messages.user_id) as username, 
                            msg,time_stamp 
                            from messages inner join channels 
                            on messages.channel_id = channels.id 
                            where messages.channel_id = :channel_id """, {
                                'channel_id' : channel_id
                            }).fetchall()
        
        for m1 in msg1:
            msgs.append({'user' : m1[0] , 'msg' : m1[1] , 'time' : m1[2]})

        #msgs = messages[channel]
        #print(msgs)
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
    sid = request.sid
    users[data['username']] = sid
    db.execute("update users set sid = :sid where username = :username",{'sid':sid,'username':data['username']})
    db.commit()
    emit('announce connected',data,broadcast=True)

@socket.on('disconnect')
def deregistersid():
    sid = request.sid
    a1 = [user for user,s in users.items() if s == sid]
    try:
        a1 = a1[0]
        # print(type(a1))
        # db.execute("update users set sid = '' where username = :username",{'username',a1})
        # db.commit()
    except IndexError:
        pass
    emit('announce disconnected',{'user':a1},broadcast=True)

@socket.on('submit msg')
def submitmsg(data):
    user = data['user']
    msg = data['msg']
    curTime = time.ctime()
    currMsg = {'user':user,'msg':msg,'time':curTime}

    try:
        msglen = len(messages[data['channel']])
        if msglen >= 100:
            messages[data['channel']].pop(0) 
        messages[data['channel']].append(currMsg)
    except KeyError:
        msglen = 0
        messages[data['channel']] = [currMsg]
    data['time'] = curTime
    
    channel_id = db.execute("select id from channels where channel_name = :channel_name", {'channel_name':data['channel']}).fetchone()
    channel_id = int(channel_id[0])

    user_id = db.execute("select id from users where username = :user_name", {'user_name':user}).fetchone()
    user_id = int(user_id[0])

    id = get_max_id("messages")

    db.execute("insert into messages (id,channel_id,user_id,time_stamp,msg) values (:id,:channel_id,:user_id,:time_stamp,:msg)", {
        'id':id,'channel_id':channel_id,'user_id':user_id,'time_stamp':curTime,'msg':msg
    })
    db.commit()
    emit('submit done',data,broadcast=True)

@socket.on('del-msg')
def delmsg(data):

    db.execute("""delete from messages where 
                time_stamp = :time_stamp 
                and msg = :msg 
                and user_id = (select id from users where username = :username)
                and channel_id = (select id from channels where channel_name = :channel_name)""", {
                    'time_stamp' : data['time'],
                    'msg' : data['msg'],
                    'username' : data['username'],
                    'channel_name' : data['channel']
                })
    db.commit()

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
    socket.run(app,port=int(os.environ["PORT"].rstrip()),debug=False)
    #socket.run(app,debug=False)
