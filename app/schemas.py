from app import ma
from app.models import Receipt


from marshmallow import fields

from marshmallow import pre_dump, post_load

class ReceiptSchema(ma.SQLAlchemyAutoSchema):
    notes = fields.String(allow_none=True)
    tags = fields.List(fields.String(), allow_none=True)

    class Meta:
        model = Receipt
        load_instance = True

    @pre_dump
    def split_tags(self, obj, **kwargs):
        # Convert comma-separated tags string to list for serialization
        if isinstance(obj.tags, str):
            obj.tags = [t.strip() for t in obj.tags.split(',') if t.strip()]
        elif obj.tags is None:
            obj.tags = []
        return obj

    @post_load
    def join_tags(self, data, **kwargs):
        # Convert list of tags to comma-separated string for DB
        tags = data.get('tags')
        if isinstance(tags, list):
            data['tags'] = ','.join([t.strip() for t in tags if t.strip()])
        return data

