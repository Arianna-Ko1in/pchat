function send() {
    newMessage($("#messageform"))
    return false;
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelector("input").onkeypress = function () {
        if (event.keyCode == 13) {
            return send();
        }
    }
    updater.start();
});

function clearMessage() {
    qs = document.querySelector("#message");
    qs.value = "";
    qs.focus();
}

function newMessage(form) {
    var message = {};
    message.body = document.querySelector("#message").value;
    message.receiver = null;
    if (document.replyto !== undefined && document.replyto!=null) {
        message.body = ' > [' + document.querySelector("#" + document.replyto).innerText + '] ' + message.body;
        message.receiver = document.replyto;
    }
    reply.style.display = 'none';
    updater.socket.send(JSON.stringify(message));
    document.replyto = null;
    clearMessage();
}

function sendTo(messageId) {
    reply = document.querySelector("#reply")
    reply.style.display = 'block';
    reply.innerText = 'In reply to: ' + document.querySelector("#" + messageId).innerText;
    document.replyto = messageId;
    clearMessage();
}

jQuery.fn.formToDict = function () {
    var fields = this.serializeArray();
    var json = {}
    for (var i = 0; i < fields.length; i++) {
        json[fields[i].name] = fields[i].value;
    }
    if (json.next) delete json.next;
    return json;
};

var updater = {
    socket: null,

    start: function () {
        var url = "ws://" + location.host + "/chatsocket";
        console.log(url);
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function (event) {
            updater.showMessage(JSON.parse(event.data));
        }
    },

    showMessage: function (message) {
        var existing = $("#m" + message.id);
        if (existing.length > 0) return;
        var node = $(message.html);
        node.hide();
        $("#inbox").append(node);
        node.slideDown();
    }
};
