import pytest

from ductus.wiki import is_legal_wiki_pagename

def test_legal_wiki_pagename():
    assert not is_legal_wiki_pagename('en', None)
    assert is_legal_wiki_pagename('en', 'somepage')
    assert is_legal_wiki_pagename('en', 'somepage_with_underscores')
    assert is_legal_wiki_pagename('en', 'somepage/with/slashes')
    assert not is_legal_wiki_pagename('en', 'somepage with spaces')
    assert not is_legal_wiki_pagename('en', 'somepage_')
    assert not is_legal_wiki_pagename('en', '_somepage')
    assert not is_legal_wiki_pagename('en', '/somepage')
    assert not is_legal_wiki_pagename('en', 'somepage/')
    assert not is_legal_wiki_pagename('en', 'some__page')
    assert not is_legal_wiki_pagename('en', '//somepage')
    assert is_legal_wiki_pagename('user', 'someuser/somepage')
    assert is_legal_wiki_pagename('user', 'someuser')
    assert not is_legal_wiki_pagename('user', '/someuser')
    assert is_legal_wiki_pagename('group', 'somegroup/somepage')
    assert is_legal_wiki_pagename('group', 'somegroup')
    assert not is_legal_wiki_pagename('group', 'somegroup//somepage')
