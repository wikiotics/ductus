from ductus.wiki.decorators import register_wiki_permission

@register_wiki_permission('user')
def user_permission_func(user, pagename):
    return (user.is_authenticated()
            and pagename.split('/', 2)[1] == user.username)
