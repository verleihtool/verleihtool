{ % load tags % }

Hi,

The request from the depot "{{ rental.depot.name }}"
requested by {{ rental.firstname }} {{ rental.lastname }}
from {{ rental.start_date }}<br />
to {{ rental.return_date }}.<br />
for the following items has been due for 7 days!

{% for item in rental.itemrental_set.all %}
* {{ item.item.quantity }}x {{ item.item.name }} from {{ item.item.location }}
{% endfor %}

We have already sent an email to {{ rental.email }}. Please change the state of the rental if the items have already been returned. 

You can click [here](http://127.0.0.1:1337/rentals/{ rental.uuid }) to review its state.

Best,
the Verleihtool
