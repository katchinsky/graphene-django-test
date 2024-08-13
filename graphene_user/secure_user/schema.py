from django.contrib.auth import get_user_model
import graphene
from graphene_django import DjangoObjectType

User = get_user_model()


def should_filter_field(name, context):
    return name == 'user' and not (context.user.is_authenticated or context.user.has_perm('auth.view_user'))


def custom_type_resolver(object_type, info, **kwargs):
    if object_type.name == "Query":
        filtered_fields = [
            (name, value) for name, value in object_type.fields.items() if not should_filter_field(name, info.context)
        ]
        return filtered_fields

    return object_type.fields


class UserType(DjangoObjectType):
    """
    Single User GraphQL Type based on Django model.
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class Query(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.Int(required=True),
                          description='Gets single User by ID')

    def resolve_user(self, info, id):
        if info.context.user.is_authenticated and info.context.user.has_perm('auth.view_user'):
            return User.objects.get(id=id)
        raise Exception('Cannot query field `user` on type `Query`')


class CustomSchema(graphene.Schema):
    def __init__(self, query):
        super().__init__(query=query)
        self.graphql_schema.type_map["__Type"].fields["fields"].resolve = custom_type_resolver


schema = CustomSchema(query=Query)
