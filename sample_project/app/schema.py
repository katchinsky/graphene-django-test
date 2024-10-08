from django.contrib.auth import get_user_model
import graphene
from graphene_django import DjangoObjectType

User = get_user_model()


def should_filter_field(name, context):
    """
    Determines whether a field should be filtered out based on the user's permissions.
    """

    return name == 'user' and not (context.user.is_authenticated and context.user.has_perm('auth.view_user'))


def permission_check_fields_resolver(object_type, info, **kwargs):
    """
    A custom resolver that filters the fields of a GraphQL type based on user permissions.
    """

    filtered_fields = [
        (name, value) for name, value in object_type.fields.items() if not should_filter_field(name, info.context)
    ]
    return filtered_fields


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
        """
        Resolves a single User object based on the provided ID, with permission checks.
        """

        if info.context.user.is_authenticated and info.context.user.has_perm('auth.view_user'):
            return User.objects.get(id=id)
        raise Exception('Cannot query field `user` on type `Query`')


class PermissionCheckSchema(graphene.Schema):
    """
    A custom GraphQL schema that enforces user permission checks on type fields.

    This schema overrides the default behavior of the GraphQL `__Type` introspection
    by injecting a custom resolver that applies user permission checks on the fields.
    """

    def __init__(self, query):
        super().__init__(query=query)
        self.graphql_schema.type_map['__Type'].fields['fields'].resolve = permission_check_fields_resolver


schema = PermissionCheckSchema(query=Query)
