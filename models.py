import enum
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def setup_models(db: SQLAlchemy):
  User = Server = Tag = SiteRole = ServerTag = ServerRolePermission = UserServerRole = ServerEvent = None
  # Base = declarative_base()
  UserServerRole = db.Table(
    'user_server_roles',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('server_id', db.Integer, db.ForeignKey('servers.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_name', db.Unicode, db.ForeignKey('server_role_permissions.role_name'))
  )

  class ServerEvent(db.Model):
    __tablename__ = 'server_events'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Unicode, nullable=True)
    name = db.Column(db.Unicode, nullable=False)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))
    # Maybe no image
    # img = db.Column

  class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, nullable=False)

  ServerTag = db.Table(
    'server_tags',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('server_id', db.Integer, db.ForeignKey('servers.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
  )

  class ServerRolePermission(db.Model):
    __tablename__ = 'server_role_permissions'
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))
    # let users give custom names to roles. 
    # Also lets them define new roles with different sets of permissions
    role_name = db.Column(db.Unicode, nullable=False)
    # read, write, etc.
    action = db.Column(db.Unicode, nullable=False)
    # Server description, server configuration files, etc.
    resource = db.Column(db.Unicode, nullable=False)

  class Server(db.Model):
    __tablename__ = 'servers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, nullable=False)
    description = db.Column(db.Unicode, nullable=True) #  nullable!
    docker_id = db.Column(db.Unicode, nullable=False)
    max_players = db.Column(db.Integer, nullable=False)
    users = db.relationship('User', secondary=UserServerRole, back_populates='servers')
    roles = db.relationship(ServerRolePermission, backref='server')
    events = db.relationship(ServerEvent, backref='sever')
    tags = db.relationship('Tag', secondary=ServerTag, backref='server')

  class SiteRole(db.Model):
    __tablename__ = 'site_roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, nullable=False)
    # view, create (purchase), etc.
    action = db.Column(db.Unicode, nullable=False)
    # Site Dashboard, servers, etc.
    resource = db.Column(db.Unicode, nullable=False)
    users = db.relationship('User', backref='site_role')

  class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.Unicode, nullable=False)
    email = db.Column(db.Unicode, nullable=False)
    username = db.Column(db.Unicode, nullable=False)
    site_role_id = db.Column(db.Integer, db.ForeignKey(SiteRole.id))
    servers = db.relationship('Server', secondary=UserServerRole, back_populates='users')

  return User, Server, Tag, SiteRole, ServerTag, ServerRolePermission, UserServerRole, ServerEvent

########################################################################
#                                   API                                #
########################################################################

def init(db: SQLAlchemy, seed: bool = False, tables=None):
  """
  Initializes the database at the given path `dbpath`. By default, no data is inserted
  to the database. `seed=True` will seed the database.
  """
  models_reset(db, seed=seed, tables=tables)
  return True

def models_reset(db: SQLAlchemy, seed: bool=False, tables=None):
  """Drops all tables and recreates them with. `seed=True` will insert dummy data into the database"""
  db.drop_all()
  db.create_all()
  if seed:
    models_seed(db, tableClasses=tables)

def models_seed(db: SQLAlchemy, tableClasses):
  (User, Server, Tag, SiteRole, ServerTag, ServerRolePermission, UserServerRole, ServerEvent) = tableClasses

  # TODO: Seed the tables with admin accounts.
  # User, Server, Tag, SiteRole, ServerTag, ServerRolePermission, UserServerRole, ServerEvent = setup_models(db)
  siteRoleOne = SiteRole(name="admin", action="create", resource="server")

  db.session.add(siteRoleOne)
  db.session.commit()
  
  siteRoles = SiteRole.query.all()
  userOne = User(username="admin", email="admin@email.com", password="admin", site_role_id=siteRoles[0].id)

  db.session.add(userOne)
  db.session.commit()

  tags = [
    Tag(name="SMP"),
    Tag(name="Vanilla"),
    Tag(name="Modded")
  ]
  db.session.add_all(tags)
  db.session.commit()

  users = User.query.all()
  tags = Tag.query.all()

  serverOne = Server(name="First Server!", description="The first server of the Minecraft Server Hosting Service, <cool and memorable name here>!", docker_id="fake docker id", max_players=20, tags=[tags[0], tags[1]])
  db.session.add(serverOne)
  db.session.commit()
  
  # serverRoles = [
  #   ServerRolePermission()
  # ]

  print(f"Implement {__file__}.seed_tables!")

# String values are persisted to db, not integer values
# may not need this
class DefaultRoleEnum(enum.Enum):
  Owner = 1
  Moderator = 2
  Developer = 3
  Member = 4
  Guest = 5

# make sure table names are correct. 
# This user on this server has this role.