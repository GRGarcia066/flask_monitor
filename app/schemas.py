from app.models import Asset, Client, Category, Topic
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class ClientSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Client
        include_relationships = True
        load_instance = True


class AssetSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Asset
        include_relationships = True
        load_instance = True


class CategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        include_relationships = True
        load_instance = True


class TopicSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Topic
        include_relationships = True
        load_instance = True


client_schema = ClientSchema()
clients_schema = ClientSchema(many=True)

asset_schema = AssetSchema()
assets_schema = AssetSchema(many=True)

category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)

topic_schema = TopicSchema()
topics_schema = TopicSchema(many=True)
