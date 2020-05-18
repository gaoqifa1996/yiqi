import tornado.ioloop
import tornado.web
import tornado.httpclient
from tornado.escape import json_encode
import json
from mod import do_post_cmd, log


class DoPut(tornado.web.RequestHandler):
    def post(self):
        try:
            ret = do_post_cmd(self.json_args["cmd"], self.json_args["data"])
        except Exception as e:
            log("put", self.json_args, e)
            ret = "Fail"

        self.write(json_encode(ret))

    def prepare(self):
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = None


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("xmljson\n\r")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/xmljson", MainHandler),
        (r"/xmljson/put", DoPut),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(9903, "127.0.0.1")

    tornado.ioloop.IOLoop.current().start()
