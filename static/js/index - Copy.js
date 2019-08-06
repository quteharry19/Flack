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

    delmsg = (elem) => {
        var data = {
            'channel' : localStorage.getItem('channel'),
            'username' : localStorage.getItem('username'),
            'msg' : elem.querySelector('.msg').innerHTML,
            'time' : elem.querySelector('.time-stamp').innerHTML
        }

        socket.emit('del-msg',data);
        
        elem.remove();
    }


    load_msg = (channel) => {

        var req = new XMLHttpRequest();

        req.open('GET',`/getmsg/${channel}`)

        req.onload = () => {
            var resp = JSON.parse(req.responseText)
            var content = template({'msgs':resp.msgs,'username':localStorage.getItem('username')})
            document.querySelector('#chatbox').innerHTML += content
            document.querySelector('#chatbox').scrollTop = document.querySelector('#chatbox').scrollHeight;
            document.querySelectorAll('.del-btn').forEach(icon => {
                icon.onclick = function() {
                    delmsg(this.parentElement);
                }
            })
            document.querySelectorAll('.chatOtherUser').forEach(name => {
                name.onclick = function() {
                    let msg = prompt('Send private message to ' + this.innerHTML)
                    alert(msg);
                }
            })

        }

        req.send();
    }
    
    load_msg(localStorage.getItem('channel'));

    socket.on('connect',() => {
        
        var username = localStorage.getItem('username');
        socket.emit('register sid',{'username':username});

    });
 
    document.querySelector('form').onsubmit = (evt) => {

        evt.preventDefault();

        return false;
    }
    
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
            document.querySelectorAll('.del-btn').forEach(icon => {
                icon.onclick = function() {
                    delmsg(this.parentElement);
                }
            });
            document.querySelectorAll('.chatOtherUser').forEach(name => {
                name.onclick = function() {
                    let msg = prompt('Send private message to ' + this.innerHTML)
                    alert(msg);
                }
            })
        
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