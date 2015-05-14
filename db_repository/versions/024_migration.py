from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
post_table = Table('post_table', pre_meta,
    Column('base', INTEGER, primary_key=True, nullable=False),
    Column('extend', INTEGER, primary_key=True, nullable=False),
)

base_post = Table('base_post', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('body', VARCHAR(length=140)),
    Column('timestamp', DATETIME),
    Column('type', VARCHAR(length=50)),
    Column('views', INTEGER),
    Column('user_id', INTEGER),
    Column('comment', INTEGER),
    Column('user_post_id', INTEGER),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['post_table'].drop()
    pre_meta.tables['base_post'].columns['user_post_id'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['post_table'].create()
    pre_meta.tables['base_post'].columns['user_post_id'].create()
