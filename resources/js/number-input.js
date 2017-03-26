// Create our own number input spinner
$('.number-up').click((ev) => {
    let $el = $(ev.target).parents('.number').find('input')
    let val = parseInt($el.val())

    $el.val(val + 1).change()
})

$('.number-down').click((ev) => {
    let $el = $(ev.target).parents('.number').find('input')
    let val = parseInt($el.val())

    $el.val(val - 1).change()
})

// Validate number inputs
$('.number input').change((ev) => {
    let val = parseInt($(ev.target).val())
    let min = parseInt($(ev.target).data('min'))
    let max = parseInt($(ev.target).data('max'))

    if (!val || val < min) {
        $(ev.target).val(min)
    }
    else if (val > max) {
        $(ev.target).val(max)
    } else {
        $(ev.target).val(val)
    }
})
