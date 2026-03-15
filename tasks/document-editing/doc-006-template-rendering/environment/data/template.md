# {{ project.name }}

**Version**: {{ project.version }}
**Author**: {{ author.name }} ({{ author.email }})
**Date**: {{ date }}

## Description

{{ project.description }}

## Features

{% for feature in features %}
- **{{ feature.name }}**: {{ feature.description }}
{% endfor %}

## Team Members

| Name | Role |
| --- | --- |
{% for member in team %}
| {{ member.name }} | {{ member.role }} |
{% endfor %}

{% if show_roadmap %}
## Roadmap

{% for milestone in roadmap %}
### {{ milestone.title }}

**Target**: {{ milestone.target_date }}

{{ milestone.description }}

{% endfor %}
{% endif %}

{% if show_license %}
## License

This project is licensed under the {{ license }} license.
{% endif %}

## Contact

For questions, reach out to {{ author.name }} at {{ author.email }}.
