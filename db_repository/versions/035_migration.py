from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user_post = Table('user_post', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('views', Integer),
    Column('comment', Integer, default=ColumnDefault(0)),
    Column('user_id', Integer),
)

base_post = Table('base_post', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('body', VARCHAR(length=140)),
    Column('timestamp', DATETIME),
    Column('type', VARCHAR(length=50)),
    Column('user_post_id', INTEGER),
    Column('comment', INTEGER),
    Column('user_id', INTEGER),
    Column('views', INTEGER),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user_post'].create()
    pre_meta.tables['base_post'].columns['comment'].drop()
    pre_meta.tables['base_post'].columns['user_id'].drop()
    pre_meta.tables['base_post'].columns['views'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user_post'].drop()
    pre_meta.tables['base_post'].columns['comment'].create()
    pre_meta.tables['base_post'].columns['user_id'].create()
    pre_meta.tables['base_post'].columns['views'].create()
