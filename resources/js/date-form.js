// show calendar prompt
$('#start_date_picker').datetimepicker({
    format: 'YYYY-MM-DD HH:mm',
    stepping: 5,
    allowInputToggle: true,
    showClose: true
})

$('#return_date_picker').datetimepicker({
    format: 'YYYY-MM-DD HH:mm',
    stepping: 5,
    allowInputToggle: true,
    showClose: true,
    useCurrent: false
})

$('#start_date_picker').on('dp.change', (e) => {
    $('#return_date_picker').data('DateTimePicker').minDate(e.date)
});

$('#return_date_picker').on('dp.change', (e) => {
    $('#start_date_picker').data('DateTimePicker').maxDate(e.date)
});
