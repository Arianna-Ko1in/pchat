#!/usr/bin/env python

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid
import tornado.options

from tornado.options import define, options

tornado.options.define("port", default=8080, help="run on the given port", type=int)

messages = {}

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/chatsocket", ChatSocketHandler),
        ]
        settings = dict(
            cookie_secret="",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
        )

        super(Application, self).__init__(handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", messages=ChatSocketHandler.cache)


class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200

    def open(self):
        ChatSocketHandler.waiters.add(self)

    def on_close(self):
        ChatSocketHandler.waiters.remove(self)
  
    @classmethod
    def send_updates(cls, chat, receiver):
        if not receiver:
            logging.info("sending message to %d waiters", len(cls.waiters))
            for waiter in cls.waiters:
                try:
                    waiter.write_message(chat)
                except:
                    logging.error("Error sending message", exc_info=True)
        else:
            logging.info("Send reply to "+receiver)
            messages[receiver].write_message(chat)

    def on_message(self, message):
        receiver = None
        logging.info("got message %r", message)
        parsed = tornado.escape.json_decode(message)
        uniq_id = str(uuid.uuid4())
        messages['m'+uniq_id] = self
        chat = {
            "id": uniq_id,
            "body": parsed["body"],
        }
        chat["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=chat))
        
        ChatSocketHandler.send_updates(chat, parsed['receiver'])


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
