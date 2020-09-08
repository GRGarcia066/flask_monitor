from flask import g
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, DateField, TimeField, IntegerField, \
    BooleanField, HiddenField, SubmitField, SelectField, widgets
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import ValidationError, DataRequired, NumberRange, IPAddress, \
    Email, EqualTo
from app.models import Project, Category, Client, User, Topic, Action
from app import Config

file_allowed = Config.ALLOWED_EXTENSIONS
csrf = CSRFProtect()


def enabled_categories():
    category_choices = []
    try:
        category_choices = Category.query.filter_by(project=g.project)
    except Exception as e:
        print(e)
    return category_choices


def existing_clients():
    client_choices = []
    try:
        client_choices = Client.query.filter_by(project=g.project)
    except Exception as e:
        print(e)
    return client_choices


def existing_actions():
    action_choices = [ 
        ("Siguiente", "Siguiente"), 
        ("Anterior", "Anterior"), 
        ("Reproducir Asset","Reproducir Asset"), 
        # ("Reproducir Categoría","Reproducir Categoría"), 
        ("Apagar/Encender", "Apagar/Encender")
    ]
    return action_choices


def existing_operations():
    operator_choices = [ 
        ("Mayor", "Mayor"), 
        ("Menor", "Menor"), 
        ("Igual", "Igual"), 
        ("Contiene" , "Contiene"), 
        ("Mayor o igual", "Mayor o igual"),
        ("Menor o igual", "Menor o igual")
    ]
    return operator_choices

def existing_protocols():
    protocol_choices = [
        ("2", "v1.2"),
        ("3", "v1.3"),
    ]
    return protocol_choices


#####################################################################################################
#                                         CUSTOM FIELDS                                             #
#####################################################################################################

class MultiCheckboxField(QuerySelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


#####################################################################################################
#                                          VALIDATORS                                               #
#####################################################################################################

class UniqueProjectName(object):
    def __init__(self, message=None):
        if not message:
            message = 'Ya existe un Proyecto con ese nombre.'
        self.message = message

                   
    def __call__(self, form, field):
        project = Project.query.filter_by(name=field.data).first()
        if project is not None:
            raise ValidationError(self.message)


class UniqueCategoryName(object):
    def __init__(self, message=None):
        if not message:
            message = 'Ya existe una Categoría con ese nombre.'
        self.message = message

                   
    def __call__(self, form, field):
        category = Category.query.filter_by(project=g.project, name=field.data).first()
        if category is not None:
            raise ValidationError(self.message)


class UniqueClientName(object):
    def __init__(self, message=None):
        if not message:
            message = 'Ya existe un Cliente con ese nombre.'
        self.message = message


    def __call__(self, form, field):
        client = Client.query.filter_by(project=g.project, name=field.data).first()
        if client is not None:
            raise ValidationError(self.message)


class UniqueAddress(object):
    def __init__(self, message=None):
        if not message:
            message = 'Ya existe un Cliente con ese IP.'
        self.message = message

       
    def __call__(self, form, field):
        client = Client.query.filter_by(project=g.project, address=field.data).first()
        if client is not None:
            raise ValidationError(self.message)


class CustomClientValidator(object):
    def __init__(self, param, message=None):
        if not message:
            message = 'Ya existe un Cliente con ese {}.'.format(param)
        self.message = message
        self.param = param
        
    
    def __call__(self, form, field):
        if self.param == "nombre":
            client = Client.query.filter_by(project=g.project, name=field.data).first()
        elif self.param == "IP":
            client = Client.query.filter_by(project=g.project, address=field.data).first()
            
        if client is not None and client.id != int(form.id.data):
            raise ValidationError(self.message)


#####################################################################################################
#                                          MQTT SETTINGS                                            #
#####################################################################################################

class MQTTSettingsForm(FlaskForm):
    client_id = StringField('Id del Cliente:')
    broker_address = StringField('Direccion Ip del Servidor:', validators=[IPAddress(ipv4=True, ipv6=False)])
    broker_port = IntegerField('Puerto del Servidor:')
    connection_timeout = IntegerField('Tiempo de espera de conexión:')
    keep_alive_interval = IntegerField('Intervalo de tiempo entre peticiones Keep Alive:')
    clean_session = BooleanField('Sesión Limpia')
    auto_reconnect = BooleanField('Reconexión automática')
    version = StringField('Versión de MQTT:')
    start_on_launch = BooleanField('Inicio automático')
    secure = BooleanField('Conexión Segura')
    tls_protocol = SelectField('Protocolo TLS:', choices=existing_protocols())
    ca_file_path = FileField('Archivo de certificado CA:', validators=[FileAllowed({'crt'}, 'Solo certificados.')])
    use_proxy = BooleanField('Usar Proxy HTTP')
    proxy_host = StringField('IP del servidor proxy:')
    proxy_port = IntegerField('Puerto del servidor proxy:')


class MQTTCredentials(FlaskForm):
    username = StringField('Nombre de usuario:', validators=[DataRequired()])
    password = PasswordField('Contraseña:', validators=[DataRequired()])
    submit = SubmitField('Enviar')


#####################################################################################################
#                                          PROJECTS                                                 #
#####################################################################################################

class ProjectForm(FlaskForm):
    name = StringField('Nombre:', validators=[DataRequired(), UniqueProjectName()])
    submit = SubmitField('Crear')


#####################################################################################################
#                                            TOPICS                                                 #
#####################################################################################################

class TopicForm(FlaskForm):
    parent = HiddenField()
    name = StringField('Nombre:', validators=[DataRequired()])
    submit = SubmitField('Crear')


#####################################################################################################
#                                          CLIENTS                                                  #
#####################################################################################################

class ClientForm(FlaskForm):
    name = StringField('Nombre:', validators=[DataRequired(), UniqueClientName()])
    address = StringField('Dirección Ip:', validators=[DataRequired(), IPAddress(ipv4=True, ipv6=False), UniqueAddress()])
    username = StringField('Nombre de usuario:')
    password = PasswordField('Contraseña:')
    submit = SubmitField('Crear')


class ClientUpdateForm(FlaskForm):
    id = HiddenField()
    name = StringField('Nombre:', validators=[CustomClientValidator("nombre")])
    address = StringField('Dirección Ip:', validators=[CustomClientValidator("IP"), IPAddress(ipv4=True, ipv6=False)])
    check_interval = IntegerField('Intervalo de actualización (segs):', validators=[NumberRange(min=5, message="Debe ser un número mayor que 5.")])  
    username = StringField('Nombre de usuario:')
    oldpassword = PasswordField('Contraseña Anterior:')
    password = PasswordField('Contraseña Nueva:')
    submit = SubmitField('Actualizar')


#####################################################################################################
#                                           ASSETS                                                  #
#####################################################################################################

class AssetForm(FlaskForm):
    category = QuerySelectMultipleField('Categorías', query_factory=enabled_categories, validators=[DataRequired()])
    upload = FileField('Seleccionar archivo...', validators=[FileRequired(), FileAllowed(file_allowed, 'Solo imágenes o videos')])
    submit = SubmitField('Crear')


class AssetUpdateForm(FlaskForm):
    startdate = DateField('Empieza:', validators=[DataRequired()])
    starttime = TimeField('Empieza:', validators=[DataRequired()])
    enddate = DateField('Termina:', validators=[DataRequired()])
    endtime = TimeField('Termina:', validators=[DataRequired()])
    duration = IntegerField('Duración en segundos:', validators=[NumberRange(min=1)])

    # all this fields are required for assets to update
    # even if we are not updating them in this form
    mimetype = HiddenField()
    is_enabled = HiddenField()
    name = HiddenField()
    play_order = HiddenField()
    nocache = HiddenField()
    uri = HiddenField()
    skip_asset_check = HiddenField()
    submit = SubmitField('Actualizar')

#####################################################################################################
#                                          CATEGORIES                                               #
#####################################################################################################

class CategoryForm(FlaskForm):
    name = StringField('Nombre:', validators=[DataRequired(), UniqueCategoryName()])
    submit = SubmitField('Crear')


class CategoryUpdateForm(FlaskForm):
    id = HiddenField()
    name = StringField('Nombre:', validators=[DataRequired(), UniqueCategoryName()])
    submit = SubmitField('Cambiar')


#####################################################################################################
#                                         SUBSCRIPTIONS                                             #
#####################################################################################################

class SubscriptionForm(FlaskForm):
    topic = StringField('Tópico:', validators=[DataRequired()])
    clients = MultiCheckboxField('Cliente(s):', query_factory=existing_clients, validators=[DataRequired()])

    # Action
    name = SelectField('Acción:', choices=existing_actions(), validators=[DataRequired()])
    operator = SelectField('Operador:', choices=existing_operations(), validators=[DataRequired()])
    value = StringField('Valor:', validators=[DataRequired()])
    extra_param_1 = QuerySelectField('Categoría:', query_factory=enabled_categories)
    extra_param_2 = StringField('Asset:')
    extra_param_3 = IntegerField('Apagar/Encender (0/1):', validators=[NumberRange(min=0, max=1)])
    submit = SubmitField('Crear')


class UpdateSubscriptionForm(FlaskForm):
    status = IntegerField()
    submit = SubmitField('Actualizar')


#####################################################################################################
#                                               AUTH                                                #
#####################################################################################################

class LoginForm(FlaskForm):
    username = StringField('Nombre de usuario:', validators=[DataRequired()])
    password = PasswordField('Contraseña:', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame:')
    submit = SubmitField('Entrar')


class RegistrationForm(FlaskForm):
    username = StringField('Nombre de usuario:', validators=[DataRequired()])
    # TODO validate emails
    # email = StringField('Correo:', validators=[DataRequired(), Email(message="Dirección de correo no valida")])
    password = PasswordField('Contraseña:', validators=[DataRequired()])
    password2 = PasswordField('Repetir Contraseña:', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('El nombre de usuario ya existe, por favor usa un nombre de usuario distinto.')


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Ya hay una cuenta con ese correo.')


class UserUpdateForm(FlaskForm):
    username = StringField('Nombre de usuario:')
    email = StringField('Correo:', validators=[Email(message="Dirección de correo no valida")])
    oldpassword = PasswordField('Contraseña:', validators=[DataRequired()])
    newpassword = PasswordField('Nueva Contraseña:')
    submit = SubmitField('Actualizar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None and user != g.current_user:
            raise ValidationError('El nombre de usuario ya existe, por favor usa un nombre de usuario distinto.')


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Ya hay una cuenta con ese correo.')
