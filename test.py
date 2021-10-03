
if __name__ == '__main__':
    from werkzeug.utils import import_string
    from config import config
    from pmgsavvsie import cronrun
    cronrun(import_string(config))

