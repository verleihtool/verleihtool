// Display items that have been selected from the depot
$('#checkout-modal').on('show.bs.modal', () => {
    // delete all items residing in the summary
    $('.rental-summary-item').remove()

    $('.rental-item').each((_, el) => {
        let selected = $(el).find('.rental-item-selected input').val()

        if (selected > 0) {
            $('.rental-summary').append(
                $('<tr class="rental-summary-item">').append(
                    $('<td>').text(
                        $(el).find('.rental-item-name').text()
                    )
                ).append(
                    $('<td>').text(
                        $(el).find('.rental-item-location').text()
                    )
                ).append(
                    $('<td>').text(selected)
                )
            )
        }
    })
})
