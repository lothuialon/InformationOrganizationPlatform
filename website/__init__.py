from flask import Flask
from flask_mail import Mail, Message

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'd3nas0k4r16780oq8prqi1231od00sadfujp1' 



    #----------
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = 'iophelperbot@gmail.com'
    app.config['MAIL_PASSWORD'] = 'jyhacixhljdmthhx'

    mail.init_app(app)

    #Blueprints
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')


    return app