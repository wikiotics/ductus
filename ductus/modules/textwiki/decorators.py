from ductus.modules.textwiki import internal_bodied_macros, internal_non_bodied_macros

def register_creoleparser_non_bodied_macro(macro_name):
    """
    register a function as a CreoleParser macro that can be called with <<macro_name>> in wikitext.
    """

    def _register_creoleparser_non_bodied_macro(func):
        internal_non_bodied_macros[macro_name] = func
        return func
    return _register_creoleparser_non_bodied_macro
