import sys
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello there'


def run():
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    app.run(threaded=True, host='0.0.0.0')


if __name__ == '__main__':
    run()
