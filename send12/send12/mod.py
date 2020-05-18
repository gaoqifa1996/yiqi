import beiqi
import ruipu
import yiqi

def get_client(model):
    if model == "beiqi":
        return beiqi.get_client()
    elif model == "ruipu":
        return ruipu.get_client()
    elif model == "yiqi":
        return yiqi.get_client()
    return None


def do_get_cmd(model, cmd, client):
    if model == "beiqi":
        beiqi.do_get_cmd(cmd, client)
    elif model == "ruipu":
        ruipu.do_get_cmd(cmd, client)
    elif model == "yiqi":
        yiqi.do_get_cmd(cmd, client)


def do_post_cmd(model, cmd, client):
    if model == "beiqi":
        beiqi.do_post_cmd(cmd, client)
    elif model == "ruipu":
        ruipu.do_post_cmd(cmd, client)
    elif model == "yiqi":
        yiqi.do_post_cmd(cmd, client)


def do_task(model):
    if model == "beiqi":
        return beiqi.do_task()
    elif model == "ruipu":
        return ruipu.do_task()
    elif model == "yiqi":
        return yiqi.do_task()

