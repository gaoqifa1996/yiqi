import tornado.ioloop
import tornado.web
import tornado.httpclient
from tornado.escape import json_encode
import json
from mod import do_post_cmd, do_task


def doTask():
    do_task()


class DoPut(tornado.web.RequestHandler):
    def post(self):
        ret = do_post_cmd(self.json_args["cmd"])

        self.write(json_encode(ret))

    def prepare(self):
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = None


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("send\n\r")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/send", MainHandler),
        (r"/send/put", DoPut),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(9900, "127.0.0.1")

    tornado.ioloop.PeriodicCallback(doTask, 1000 * 30).start()
    tornado.ioloop.IOLoop.current().start()
