$('table.table-clickable tr.row-clickable').click(function () {
    let href = $(this).data('href')

    if (href) {
        window.location.href = href
    }
})
