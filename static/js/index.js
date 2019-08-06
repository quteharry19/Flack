var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

document.addEventListener('DOMContentLoaded', () => {
    var template = Handlebars.compile(document.querySelector('#chatscript').innerHTML)

    clearText = () => {
        document.querySelector('h5').innerHTML = '';
    }
    var clsText = setTimeout(clearText,5000);
    Handlebars.registerHelper('if_equal',function(a,b,options) {
        if (a === b){
            // alert('check users ' + a + ' ' + b );
            return options.fn(this);
        } else {
            return options.inverse(this);
        }
    });

    document.querySelector('#uploadForm').onsubmit = () =>{
        document.querySelector('#uploadUser').value = localStorage.getItem('username');
        document.querySelector('#uploadChannel').value = localStorage.getItem('channel');
    }

    document.querySelectorAll('.channel').forEach( channel => {
        channel.onclick = () => {
            document.querySelector('#chatbox').innerHTML = '';
            document.querySelector('#channelname').innerHTML = channel.dataset.channel;
            document.querySelector('#formchannel').style.display = 'none';
            document.querySelector('.container').className = "container x-open-sidebar";
            localStorage.setItem('channel',channel.dataset.channel);
            load_msg(channel.dataset.channel);
            return false;
        }
    });

    document.querySelector('#createchannel').onclick = () => {
        document.querySelector('#formchannel').style.display = 'block';
    }    

    delmsg = () => {
        document.querySelectorAll('.del-btn').forEach(icon => {
            icon.onclick = function() {
                let data = {
                    'channel' : localStorage.getItem('channel'),
                    'username' : localStorage.getItem('username'),
                    'msg' : this.parentElement.querySelector('.msg').innerHTML,
                    'time' : this.parentElement.querySelector('.time-stamp').innerHTML
                }
        
                socket.emit('del-msg',data);
                
                this.parentElement.remove();
            }
        })

    }

    pvtChat = () => {
        document.querySelectorAll('.chatOtherUser').forEach(name => {
            name.onclick = function() {
                toName = this.firstElementChild.textContent;
                let msg = prompt('Send private message to : ' + toName)
                if (msg!=null && msg!=''){
                    payload = {
                        'msg' : msg,
                        'toUser' : toName,
                        'fromUser': localStorage.getItem('username')
                    }
                    socket.emit('pvt msg',payload);
                } else {
                    alert('message content is null');
                }
            }
        })
    }

    load_msg = (channel) => {

        var req = new XMLHttpRequest();

        req.open('GET',`/getmsg/${channel}`)

        req.onload = () => {
            var resp = JSON.parse(req.responseText);
            var content = template({'msgs':resp.msgs,'username':localStorage.getItem('username')});
            document.querySelector('#chatbox').innerHTML += content;
            document.querySelector('#chatbox').scrollTop = document.querySelector('#chatbox').scrollHeight;
            delmsg();
            pvtChat();
        }

        req.send();
    }
    
    load_msg(localStorage.getItem('channel'));

    document.querySelector('#newChannelSubmit').onclick = () => {
        let newChannelName = document.querySelector('#newChannelName').value;
        if (newChannelName != ''){
            localStorage.setItem('channel',newChannelName);
        }
    }

    document.querySelector('#formClose').onclick = () => {
        document.querySelector('#formchannel').style.display = 'none';
    }

    socket.on('connect',() => {
        
        let username = localStorage.getItem('username');
        let channel = localStorage.getItem('channel');
        socket.emit('register sid',{'username':username,'channel':channel});
    });


    socket.on('pvt msg done', (data) => {
        let username = localStorage.getItem('username');
        if (username == data.toUser){
            alert('Message from ' + data.fromUser + ' : ' + data.msg);
        }
    })

    socket.on('pvt msg offline', (data) => {
        let username = localStorage.getItem('username');
        if (username == data.fromUser){
            alert('Your Message was undelivered :' + data.toUser + ' is offline now');
        }
    })
    socket.on('announce connected',(data)=>{
        let username = localStorage.getItem('username');
        let channel = localStorage.getItem('channel');

        document.querySelectorAll('.chatbubbleUserName').forEach(user => {
            if (user.innerHTML == data.username){
                user.style.color = 'green';
            }
        })

        if (channel == data.channel && username != data.username ){
            document.querySelector('#chatbox').innerHTML += 'User ' + data.username + ' joined now'
            document.querySelector('#chatbox').scrollTop = document.querySelector('#chatbox').scrollHeight;
        }
    })

    socket.on('announce disconnected', (data)=>{
        alert(data.user + ' disconnected');
    })
    
    document.querySelector('#sendmsg').onclick = () =>{
        if (document.querySelector('#msgText').value != ''){
            sendmsg() ;
            document.querySelector('#msgText').value = '';
        }
    }
    
    document.querySelector('#msgText').onkeypress = (evt) => {

        if (evt.key === 'Enter'){
            if (document.querySelector('#msgText').value != ''){
                sendmsg() ;
                document.querySelector('#msgText').value = '';
            }
        }
    }

    sendmsg = () => {

        var channel = localStorage.getItem('channel')
        var username = localStorage.getItem('username');
        var msg = document.querySelector('#msgText').value;

        socket.emit('submit msg',{'channel':channel,'user':username,'msg':msg})
    }

    socket.on('submit done', (msg) => {
        
        if (localStorage.getItem('channel') == msg.channel){
            var content = template({'msgs':[msg],'username':localStorage.getItem('username')});
            document.querySelector('#chatbox').innerHTML += content ;

            delmsg();      
            pvtChat();

            document.querySelector('#chatbox').scrollTop = document.querySelector('#chatbox').scrollHeight;
        }        
    });

    socket.on('del-msg done',(msg) => {
        if (localStorage.getItem('channel') == msg.channel ){
            document.querySelectorAll('.messages').forEach(msgDiv => {
                if (msgDiv.querySelector('.time-stamp').innerHTML == msg.time && msgDiv.querySelector('.msg').innerHTML == msg.msg && msgDiv.querySelector('.chatbubbleUserName').innerHTML == msg.user ){
                    msgDiv.remove();
                }
            });
        }
    });

});