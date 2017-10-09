$('table.table-clickable tr.row-clickable').click(function(ev) {
    let href = $(this).data('href')

    if (href) {
        if (ev.ctrlKey || ev.metaKey) {
            window.open(href, '_blank')
        } else {
            window.location.href = href
        }
    }
})
