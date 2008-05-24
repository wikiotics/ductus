var picture_urns = [{% for urn in object.pictures %}'{{ urn }}'{% if not forloop.last %}, {% endif %}{% endfor %}];
