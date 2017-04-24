// Only enable checkout button when items are selected
$('.rental-item-selected input').change(() => {
    let sum = 0

    $('.rental-item-selected input').each((_, el) => {
        sum += $(el).val()
    })

    $('#checkout-button').attr('disabled', sum <= 0)
})

// Display items that have been selected from the depot
$('#checkout-modal').on('show.bs.modal', () => {
    // delete all items residing in the summary
    $('.rental-summary-item, .rental-summary-item-input').remove()

    $('.rental-item').each((_, el) => {
        let $input = $(el).find('.rental-item-selected input')
        let selected = $input.val()

        if (selected > 0) {
            $('.rental-summary').append(
                $('<tr>', {class: 'rental-summary-item'}).append(
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

            $('#checkout-form').append(
                $('<input>', {
                    type: 'hidden',
                    name: $input.data('name'),
                    class: 'rental-summary-item-input',
                    value: selected
                })
            )
        }
    })
})
