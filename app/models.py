from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash


login = LoginManager()
db = SQLAlchemy()


assets_cat_table = db.Table('assets_cat_table', 
                       db.Column('asset_id', db.String(64), db.ForeignKey('category.id'), nullable=False),
                       db.Column('category_id',  db.Integer, db.ForeignKey('asset.id'), nullable=False),
                       db.PrimaryKeyConstraint('asset_id', 'category_id'))


clients_assets_table = db.Table('clients_assets_table', 
                       db.Column('client_id', db.Integer, db.ForeignKey('client.id'), nullable=False),
                       db.Column('asset_id',  db.String(64), db.ForeignKey('asset.id'), nullable=False),
                       db.PrimaryKeyConstraint('client_id', 'asset_id'))


clients_actions_table = db.Table('clients_actions_table', 
                       db.Column('client_id', db.Integer, db.ForeignKey('client.id'), nullable=False),
                       db.Column('action_id',  db.Integer, db.ForeignKey('action.id'), nullable=False),
                       db.PrimaryKeyConstraint('client_id', 'action_id'))


client_subs_table = db.Table('client_subs_table', 
                       db.Column('client_id', db.Integer, db.ForeignKey('client.id'), nullable=False),
                       db.Column('subscription_id',  db.Integer, db.ForeignKey('subscription.id'), nullable=False),
                       db.PrimaryKeyConstraint('client_id', 'subscription_id'))


#####################################################################################################
#                                          PROJECTS                                                 #
#####################################################################################################

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    topics = db.relationship("Topic", backref=db.backref("project", uselist=False))
    clients = db.relationship('Client', backref=db.backref('project', uselist=False))
    assets = db.relationship('Asset', backref=db.backref('project', uselist=False))
    categories = db.relationship('Category', backref=db.backref('project', uselist=False))
    subscriptions = db.relationship('Subscription', backref=db.backref('project', uselist=False))


    def __repr__(self):
        return self.name


#####################################################################################################
#                                            TOPICS                                                 #
#####################################################################################################

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    subtopic = db.relationship("Topic", backref=db.backref('parent', remote_side=[id]))


    def is_root(self):
        return self.parent_id == None

    
    def is_leaf_node(self):
        return self.subtopic == None


    def __repr__(self):
        if self.is_root():
            return self.name
        return "{}/{}".format(str(self.parent), self.name)


#####################################################################################################
#                                          CLIENTS                                                  #
#####################################################################################################

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    address = db.Column(db.String(64), index=True, unique=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    assets = db.relationship('Asset', secondary=clients_assets_table, backref=db.backref('clients'))
    actions = db.relationship('Action', secondary=clients_actions_table, backref=db.backref('clients'))

    # Others
    check_interval = db.Column(db.Integer)
    username = db.Column(db.String(64), default='')
    password = db.Column(db.String(128), default='')


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return self.name


#####################################################################################################
#                                           ASSETS                                                  #
#####################################################################################################

class Asset(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(256))
    filename = db.Column(db.String(256))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    categories = db.relationship('Category', secondary=assets_cat_table, backref=db.backref('assets'))


    def is_image(self):
        return self.filename.lower().endswith(('.png', '.jpg', '.jpeg'))


    def is_video(self):
        return self.filename.lower().endswith(('.mp4', '.mpg', '.avi'))


    def __repr__(self):
        return 'Asset {}'.format(self.filename)


#####################################################################################################
#                                          CATEGORIES                                               #
#####################################################################################################

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    def __repr__(self):
        return self.name


#####################################################################################################
#                                         SUBSCRIPTIONS                                             #
#####################################################################################################

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(128))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    actions = db.relationship('Action', backref=db.backref('subscription', uselist=False), cascade="all, delete") 
    status = db.Column(db.Integer)


#####################################################################################################
#                                            ACTIONS                                                #
#####################################################################################################

class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    operator = db.Column(db.Integer)
    value = db.Column(db.String(32))
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'))
    extra_param_1 = db.Column(db.String(32))
    extra_param_2 = db.Column(db.String(32))
    extra_param_3 = db.Column(db.String(32))


    def __repr__(self):
        return self.name


#####################################################################################################
#                                             AUTH                                                  #
#####################################################################################################

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
