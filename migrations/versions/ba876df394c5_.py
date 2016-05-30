"""Add unique constraint to prevent duplicate menu entries.

Enforce a unique combination of date_valid, description, mensa, and category.
This way, if the scraper is run more than once on the same menu, it should not
be able to accidentally save the same exact entry twice.
Revision ID: ba876df394c5
Revises: e106ab7b8607
Create Date: 2016-05-30 20:44:08.687457

"""

# revision identifiers, used by Alembic.
revision = 'ba876df394c5'
down_revision = 'e106ab7b8607'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # batch_alter_table() is necessary here because SQLite does not support
    # the SQL ALTER statement which would normally be emitted here.

    # What this function does is basically cause all the data in the old
    # version of the table to be copied into a new table, then delete the old
    # table at the end if everything works as planned.
    with op.batch_alter_table('menu_entries') as batch_op:
        batch_op.create_unique_constraint(
            constraint_name="unique_menu_entry_date_mensa_category_description",
            columns=['date_valid', 'mensa', 'category', 'description'])


def downgrade():
    with op.batch_alter_table('menu_entries') as batch_op:
        batch_op.drop_constraint(
            constraint_name="unique_menu_entry_date_mensa_category_description",
            type_='unique')
