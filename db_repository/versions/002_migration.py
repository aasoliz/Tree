from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
post = Table('post', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('body', VARCHAR(length=140)),
    Column('timestamp', DATETIME),
    Column('user_id', INTEGER),
)

base_post = Table('base_post', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('body', String(length=140)),
    Column('timestamp', DateTime),
    Column('type', String(length=50)),
    Column('views', Integer),
    Column('user_id', Integer),
)

user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('nickname', String(length=64)),
    Column('age', Integer),
    Column('email', String(length=120)),
    Column('last_seen', DateTime),
    Column('about_me', String(length=140)),
    Column('reputation', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['post'].drop()
    post_meta.tables['base_post'].create()
    post_meta.tables['user'].columns['age'].create()
    post_meta.tables['user'].columns['last_seen'].create()
    post_meta.tables['user'].columns['reputation'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['post'].create()
    post_meta.tables['base_post'].drop()
    post_meta.tables['user'].columns['age'].drop()
    post_meta.tables['user'].columns['last_seen'].drop()
    post_meta.tables['user'].columns['reputation'].drop()
