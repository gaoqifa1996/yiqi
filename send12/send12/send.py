import tornado.ioloop
import tornado.web
import tornado.httpclient
from tornado.escape import json_encode
import json
from tool import init_log, get_model, do_compress
from mod import get_client, do_get_cmd, do_post_cmd, do_task
import time


def doTask():
    model = get_model()
    do_task(model)



def doCompress():
    do_compress()


class DoGet(tornado.web.RequestHandler):
    def post(self):
        model = get_model()
        client = get_client(model)
        ret = do_get_cmd(model, self.json_args["cmd"], client)
        print(ret)

    def prepare(self):
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = None


class DoPut(tornado.web.RequestHandler):
    def post(self):
        model = get_model()
        client = get_client(model)
        ret = do_post_cmd(model, self.json_args["cmd"], client)

        self.write(json_encode(ret))

    def prepare(self):
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = None


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("send gao\n\r")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/send", MainHandler),
        (r"/send/put", DoPut),
        (r"/send/get", DoGet),
    ])




if __name__ == "__main__":
    init_log()

    app = make_app()
    app.listen(9900, "127.0.0.1")

    tornado.ioloop.PeriodicCallback(doTask, 1000 * 20).start()


    tornado.ioloop.PeriodicCallback(doCompress, 1000 * 60 * 60 * 2).start()


    tornado.ioloop.IOLoop.current().start()
