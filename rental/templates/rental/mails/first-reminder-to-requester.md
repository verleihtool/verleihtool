{% load tags %}

Hello {{ rental.firstname }} {{ rental.lastname }},

your rented items from 
{{ rental.start_date }} to {{ rental.return_date }} 
have been due since 7 days!

{% for item in rental.itemrental_set.all %}
* {{ item.item.quantity }}x {{ item.item.name }} from {{ item.item.location }}
{% endfor %}

Visit this [link](http://127.0.0.1:1337/rentals/{ rental.uuid }) to view the items that you have to bring back!

Best,
the Verleihtool
