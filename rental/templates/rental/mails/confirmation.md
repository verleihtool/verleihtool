{% load tags %}

Hello {{ rental.firstname }} {{ rental.lastname }},

here is a summary of your rental request lasting from
{{ rental.start_date }} to {{ rental.return_date }}.

{% for item in rental.itemrental_set.all %}
* {{ item.item.quantity }}x {{ item.item.name }}
{% endfor %}

You can view the status of your request here:

<{% base_url %}{% url 'rental:detail' rental_uuid=rental.uuid %}>

Best,
the Verleihtool
