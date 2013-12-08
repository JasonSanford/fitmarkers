from django.contrib.auth.models import User
import factory


firsts = ('Jason', 'Ellen', 'Ethan', 'Elliott',)
lasts = ('Sanford', 'Crafton', 'Edwin', 'Zubich',)

class UserFactory(factory.Factory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: 'user{0}'.format(n))