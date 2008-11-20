var picture_urns = [{% for urn in object.pictures %}'{{ urn }}'{% if not forloop.last %}, {% endif %}{% endfor %}];
var correct_urn = '{{ object.correct_picture }}';
