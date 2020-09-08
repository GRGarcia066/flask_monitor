import time, threading, logging, re
import paho.mqtt.client as mqtt
from threading import Thread
from app.models import Subscription, Action
from app.screenly_api import control_asset, turn_on_off
import xml.etree.ElementTree as ET
import os


mqtt_connection_errors = {
    1: "Conexión rechazada: versión de protocolo incorrecta.",
    2: "Conexión rechazada: identificador de cliente no válido.",
    3: "Conexión rechazada: servidor no disponible.",
    4: "Conexión rechazada: nombre de usuario o contraseña incorrectos.",
    5: "Conexión rechazada: no autorizado."
}


mqtt_controls = {
    0: "STOP SUBSCRIPTIONS",
    1: "START SUBSCRIPTIONS",
    2: "RESTART SUBSCRIPTIONS"
}


def text_to_re(text):
    if "+" in text:
        return text.replace("+", "(\\w+)")
    elif "#" in text:
        return "^{}".format(text).replace("/#", "")
    return text


def print_message(message):
    logging.debug("Message <{}> received from topic <{}>".format(str(message.payload.decode("utf-8")), message.topic))
    logging.debug("Message QoS: {}.".format(str(message.qos)))
    logging.debug("Message retain flag: {}.\n".format(message.retain))


def print_action(action):
    logging.debug("Action Name: {}".format(action.name))
    logging.debug("Action Operator: {}.".format(action.operator))
    logging.debug("Action Value: {}.\n".format(action.value))


def check_operation(operator, expected_value, value):
    try:
        if operator == "Mayor":
            return int(value) > int(expected_value)
        if operator == "Mayor o igual":
            return int(value) > int(expected_value) or int(value) == int(expected_value)
        if operator == "Menor":
            return int(value) < int(expected_value)
        if operator == "Menor o igual":
            return int(value) < int(expected_value) or int(value) == int(expected_value)
        if operator == "Igual":
            return int(value) == int(expected_value)
        if operator == "Contiene":
            return str(value) in str(expected_value)
    except Exception:
        pass
    return False


def handle_action_next(action, client):
    logging.debug("Sending action next to client {}".format(client.name))
    if client is not None:
        control_asset(client, "next")


def handle_action_prev(action, client):
    logging.debug("Sending action prev to client {}".format(client.name))
    if client is not None:
        control_asset(client, "previous")


def handle_action_set_asset(action, client):
    logging.debug("Sending action set asset to client {}".format(client.name))
    if client is not None:
        control_asset(client, "asset&{}".format(action.extra_param_2))


def handle_action_turn(action, client):
    logging.debug("Sending action turn to client {}".format(client.name))
    if client is not None:
        turn_on_off(client, action.extra_param_3)


def handle_action(action, client, message):
    print_action(action)
    logging.debug("Checking operation...")
    if check_operation(action.operator, action.value, message):
        if action.name == "Siguiente":
            handle_action_next(action, client)
        elif action.name == "Anterior":
            handle_action_prev(action, client)
        elif action.name == "Reproducir Asset":
            handle_action_set_asset(action, client)
        elif action.name == "Apagar/Encender":
            handle_action_turn(action, client)
    else:
        logging.debug("Unhandled..")


class ScreenlyMQTTClient(mqtt.Client):

    def __init__(self,  *args, **kwargs):
        super(ScreenlyMQTTClient, self).__init__(*args, **kwargs)
        self.subscriptions_dict = {}
        self.wildcards_dict = {}
        self.topics = list()
        self.topic_ack = []
        self.connected_flag = False
        self.bad_connection_flag = False
        self.disconnected_flag= False
        self.conn_err = None


    def __update_settings(self, app):
        self._client_id = app.config["MQTT_CLIENT_ID"]
        self._clean_session = app.config['MQTT_CLEAN_SESSION'] == "1"
        self.broker_address = app.config['MQTT_BROKER_ADDRESS']
        self.port = int(app.config['MQTT_BROKER_PORT'])
        self.keepalive = int(app.config['MQTT_KEEP_ALIVE_INTERVAL'])
        self.tls_version = int(app.config['MQTT_TLS_PROTOCOL'])
        
        path = app.config['BASE_DIR']
        if self._ssl_context is None and app.config['MQTT_SSL/TLS'] == "1":
            ca_path = os.path.join(path, 'certs', app.config['MQTT_CA_FILE_PATH'])
            if os.path.exists(ca_path):
                self.tls_set(ca_path, tls_version=self.tls_version)       
                self.tls_insecure_set(True) # overrides name checking as a temporary measure


    def init_app(self, app):
        path = app.config['BASE_DIR']
        conf_path = os.path.join(path, 'config.xml')
        tree = ET.parse(conf_path)
        root = tree.getroot()
        mqtt_config = root.find("config/[@type='mqtt']")
        for elem in mqtt_config:
            name = elem.get('name')
            value = elem.get('value')
            app.config[name] = value
        app.config['MQTT_PASSWORD_PROTECTED'] = "0"
        self.__update_settings(app)


    def update_settings(self, app):
        path = app.config['BASE_DIR']
        conf_path = os.path.join(path, 'config.xml')
        tree = ET.parse(conf_path)
        root = tree.getroot()
        mqtt_config = root.find("config/[@type='mqtt']")
        for elem in mqtt_config:
            name = elem.get('name')
            value = elem.get('value')
            new_value = str(app.config[name])
            if new_value != value:
                elem.set('value', new_value)
        tree.write(conf_path)
        self.__update_settings(app)

        
    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            self.connected_flag=True
            self.disconnected_flag=False
            self.bad_connection_flag=False
            logging.debug("Connected OK Returned Code: {}".format(rc))
        else:
            self.bad_connection_flag=True
            self.connected_flag=False
            self.disconnected_flag=False
            self.conn_err = mqtt_connection_errors[rc]
            logging.critical("Returned Code: {}".format(self.conn_err))


    def on_disconnect(self, client, userdata, rc):
        self.disconnected_flag=True
        self.connected_flag=False
        self.bad_connection_flag=False

        if rc == 0:
            logging.debug("Disconnected normally")
        else:
            self.conn_err = mqtt.error_string(rc)
            logging.critical(self.conn_err)


    def on_subscribe(self, client, userdata, mid, granted_qos):
        """
        Removes mid values from subscribe list
        """
        if len(client.topic_ack)==0:
            logging.debug("All subscriptions acknowledged")
            return

        for index, t in enumerate(client.topic_ack):
            if t[1]==mid:
                client.topic_ack.pop(index)
                logging.debug("Successfully subscribed to topic {}".format(t[0]))


    def on_unsubscribe(self, client, userdata, mid):
        logging.debug("Unsubscription <Mid: {}>".format(mid))


    def check_wildcards(self, topic):
        for wildcard in self.wildcards_dict.keys():
            ptrn = re.compile(wildcard)
            matched_obj = ptrn.match(topic)
            if matched_obj is not None:
                return self.wildcards_dict[wildcard]
        return None


    def on_message(self, client, userdata, message):
        print_message(message)

        if message.topic in self.subscriptions_dict:
            actions_and_clients = self.subscriptions_dict.get(message.topic)
        else:
            actions_and_clients = self.check_wildcards(message.topic)
       
        if actions_and_clients is not None:         
            message = str(message.payload.decode("utf-8"))
            for action, clients in actions_and_clients:
                for client in clients:
                    Thread(target=handle_action, kwargs={ "action": action, "client": client, "message": message }).start()


    def try_subscribe(self, topic):
        try:
            result, mid = self.subscribe(topic)
            if result == 0:
                self.topic_ack.append((topic, mid))
            else:
                err_string = mqtt.error_string(result)
                logging.critical("Could not subscribe to topic {}. Error code {}.".format(topic, err_string))
        except Exception as e:
            logging.critical(e)


    def load_subscriptions(self, subscriptions):
        for subscription in subscriptions:
            topic = subscription.topic
            if topic in self.topics:
                message = "Ya existe una suscripción al tópico {}.".format(topic)
                logging.critical(message)
                raise Exception(message)

            self.topics.append(topic)
            if "+" in topic or "#" in topic:
                topic = text_to_re(topic)
                self.wildcards_dict[topic] = []
                for action in subscription.actions:
                    self.wildcards_dict[topic].append((action, action.clients))
            else:
                self.subscriptions_dict[topic] = []
                for action in subscription.actions:
                    self.subscriptions_dict[topic].append((action, action.clients))

            if self.connected_flag:
                for topic in self.topics:
                    self.try_subscribe(topic)
        logging.debug("Loaded {} subscription(s)".format(len(subscriptions)))


    def __remove_subscription(self, subscription):
        if subscription.topic in self.subscriptions_dict:
            self.subscriptions_dict.pop(subscription.topic)
        elif subscription.topic in self.wildcards_dict:
            self.wildcards_dict.pop(subscription.topic)
        if subscription.topic in self.topics:
            self.topics.remove(subscription.topic)
        self.unsubscribe(subscription.topic)


    def remove_subscription(self, subscription):
        self.__remove_subscription(subscription)


    def update_subscription(self, subscription):
        topic = subscription.topic
        if not topic in self.topics:
            return

        if "+" in topic or "#" in topic:
            topic = text_to_re(topic)
            if topic in self.wildcards_dict:
                self.wildcards_dict[topic] = []
                for action in subscription.actions:
                    self.wildcards_dict[topic].append((action, action.clients))

        elif topic in self.subscriptions_dict:
            self.subscriptions_dict[topic] = []
            for action in subscription.actions:
                self.subscriptions_dict[topic].append((action, action.clients))


    def unsubscribe_project(self, project):
        for subscription in project.subscriptions:
            self.__remove_subscription(subscription)


    def start(self):
        if self.connected_flag:
            return

        logging.debug("Starting MQTT Client...")
        self.connect(self.broker_address, port=self.port, keepalive=self.keepalive)
        self.loop_start()

        while not self.connected_flag and not self.bad_connection_flag:
            logging.debug("Connecting to broker server...")
            time.sleep(1)
            if self.disconnected_flag:
                self.loop_stop()
                raise Exception(self.conn_err)

        if self.bad_connection_flag:
            self.loop_stop()
            raise Exception(self.conn_err)

        logging.debug("Connected, subscribing...")
        if len(self.topics) > 0:
            for topic in self.topics:
                self.try_subscribe(topic)
        else:
            logging.debug("No topics to subscribe.")


    def stop(self):
        if not self.connected_flag:
            return        
        logging.debug("Sending Stop...")
        self.loop_stop()
        logging.debug("Connection loop stopped...")
        self.disconnect()
        logging.debug("Disconnecting...")


mqtt_client = ScreenlyMQTTClient()
