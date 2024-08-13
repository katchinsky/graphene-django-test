from django.contrib.auth.models import Permission
from graphene.test import Client
from django.test import TestCase
from graphene_user.secure_user.schema import schema, User
from collections import namedtuple


class PermissionCheckTestCase(TestCase):
    def setUp(self):
        self.client = Client(schema=schema)
        self.user_with_perms = User.objects.create_user('user_with_perms')
        self.user_with_perms.user_permissions.add(Permission.objects.get(codename='view_user'))
        self.user_without_perms = User.objects.create_user('user_without_perms')

    def test_user_query(self):
        query = '''
            query {
                 user(id: 1) {
                      username
                      email
                }
            }
            '''

        context = namedtuple('Context', ['user'])

        response = self.client.execute(
            query, context_value=context(user=self.user_with_perms)
        )

        self.assertEqual(response['data'], {'user': {'username': 'user_with_perms', 'email': ''}})

        response = self.client.execute(
            query, context_value=context(user=self.user_without_perms)
        )
        self.assertIn('errors', response)
        self.assertEqual(response['errors'][0]['message'], 'Cannot query field `user` on type `Query`')

    def test_introspection_query(self):
        query = '''
            query  {
                  type: __type(name: "Query") {
                    fields {
                      name
                      description
                    }
                  }
            }
        '''
        context = namedtuple('Context', ['user'])

        response = self.client.execute(
            query, context_value=context(user=self.user_with_perms)
        )

        self.assertEqual(response['data'],
                         {'type': {'fields': [{'name': 'user', 'description': 'Gets single User by ID'}]}})

        response = self.client.execute(
            query, context_value=context(user=self.user_without_perms)
        )
        self.assertEqual(response['data'], {'type': {'fields': []}})
