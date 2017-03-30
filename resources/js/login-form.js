// Focus the username input when clicking Login
$('#login-dropdown').on('shown.bs.dropdown', (ev) => {
    $(ev.target).find('#username').focus()
})
