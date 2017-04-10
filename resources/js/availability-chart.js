let Chart = require('chart.js')

let availabilityChart = null

$('#availability-modal').on('show.bs.modal', (ev) => {
    let name = $(ev.relatedTarget).parents('.rental-item').data('name')

    $('#availability-item').text(name)
})

$('#availability-modal').on('shown.bs.modal', (ev) => {
    let $chart = $('#availability-chart');
    let intervals = $(ev.relatedTarget).parents('.rental-item').data('intervals')
    let maxAvailability = intervals.reduce(
        (val, acc) => val.y > acc.y ? val.y : acc.y
    )

    availabilityChart = new Chart($chart, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Availability',
                data: intervals,
                backgroundColor: 'rgba(51, 122, 183, 0.4)',
                borderColor: 'rgba(46, 109, 164, 1)',
                steppedLine: true,
                borderDashOffset: 0.0,
            }]
        },
        options: {
            layout: {
                padding: {
                    left: 50
                }
            },
            legend: {
                position: 'bottom'
            },
            scales: {
                xAxes: [{
                    type: 'time',
                    time: {
                        minUnit: 'hour'
                    }
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        suggestedMax: maxAvailability + 1
                    }
                }]
            }
        }
    })
})

$('#availability-modal').on('hidden.bs.modal', (ev) => {
    if (availabilityChart !== null) {
        availabilityChart.destroy()
    }
})
