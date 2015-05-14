from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
base_post = Table('base_post', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('body', String(length=140)),
    Column('timestamp', DateTime),
    Column('user_post_id', Integer),
    Column('type', String(length=50)),
    Column('views', Integer),
    Column('comment', Integer, default=ColumnDefault(0)),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['base_post'].columns['user_id'].create()
    post_meta.tables['base_post'].columns['views'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['base_post'].columns['user_id'].drop()
    post_meta.tables['base_post'].columns['views'].drop()
