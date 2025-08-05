import logging

def setup_logger(app):
    handler = logging.FileHandler('access.log')
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    @app.before_request
    def log_request():
        app.logger.info(f"{request.method} {request.path} from {request.remote_addr}")