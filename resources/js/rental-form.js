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

// show calendar prompt
$('#start_date_picker').datetimepicker({
    format: 'YYYY-MM-DD HH:mm',
    stepping: 5,
    allowInputToggle: true,
    minDate: new Date()
})

$('#end_date_picker').datetimepicker({
    format: 'YYYY-MM-DD HH:mm',
    stepping: 5,
    allowInputToggle: true,
    useCurrent: false
})

$('#start_date_picker').on('dp.change', (e) => {
    $('#end_date_picker').data('DateTimePicker').minDate(e.date)
});

$('#end_date_picker').on('dp.change', (e) => {
    $('#start_date_picker').data('DateTimePicker').maxDate(e.date)
});
