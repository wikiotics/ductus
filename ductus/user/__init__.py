from ductus.wiki.decorators import register_wiki_permission

@register_wiki_permission('user')
def user_permission_func(user, pagename):
    return (user.is_authenticated()
            and pagename.split('/', 2)[1] == user.username)

from django.contrib.auth.models import User

# fix User.get_absolute_url() to point to the right place
User.get_absolute_url = lambda self: '/user/%s' % self.username
