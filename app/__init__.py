from flask import Flask
from config import Config, UnitTestConfig
import logging


def create_app(testing=False):
    app = Flask(__name__, static_folder="static", template_folder="templates")

    if testing:
        app.config.from_object(UnitTestConfig)
    else:
        app.config.from_object(Config)

    from app.forms import csrf
    csrf.init_app(app)

    from app.models import db, User, Subscription
    db.init_app(app)

    from app.models import login
    login.init_app(app)
    login.login_view = '/auth/login'

    with app.app_context():
        db.create_all()      
        if User.query.count() == 0:
            user = User(username="admin")     
            user.set_password("admin")
            db.session.add(user)
            db.session.commit()

        from app.routes import auth, general, projects, assets, clients, categories, \
            topics, subscriptions, mqtt

        app.register_blueprint(auth.bp)
        app.register_blueprint(general.bp)
        app.register_blueprint(projects.bp)
        app.register_blueprint(assets.bp)
        app.register_blueprint(clients.bp)
        app.register_blueprint(categories.bp)
        app.register_blueprint(topics.bp)
        app.register_blueprint(subscriptions.bp)
        app.register_blueprint(mqtt.bp)

        from app.mqtt import mqtt_client
        mqtt_client.init_app(app)

        if app.config["MQTT_START_ON_LAUNCH"] == "1" and Subscription:
            subscriptions = Subscription.query.filter_by(status=1).all()
            if len(subscriptions) > 0:       
                mqtt_client.load_subscriptions(subscriptions)
                try:
                    mqtt_client.start()
                except Exception:                  
                    pass # error should log by it self

    return app
