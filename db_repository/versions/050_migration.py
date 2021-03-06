from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
base_post = Table('base_post', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('body', String(length=500)),
    Column('timestamp', DateTime),
    Column('category', String),
    Column('type', String(length=50)),
    Column('views', Integer, default=ColumnDefault(0)),
    Column('extend', Integer, default=ColumnDefault(0)),
    Column('comment', Integer, default=ColumnDefault(0)),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['base_post'].columns['body'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['base_post'].columns['body'].drop()
