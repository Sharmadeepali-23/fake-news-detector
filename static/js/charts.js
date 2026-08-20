document.addEventListener('DOMContentLoaded', () => {
    const trendCanvas = document.getElementById('trendChartCanvas');
    const pieCanvas = document.getElementById('pieChartCanvas');

    if (!trendCanvas || !pieCanvas) return;

    fetch('/admin/stats-json')
        .then(response => response.json())
        .then(data => {
            initTrendChart(trendCanvas, data.trend_labels, data.real_daily, data.fake_daily);
            initPieChart(pieCanvas, data.pie_data);
        })
        .catch(err => console.error('Failed to load chart data:', err));

    function initTrendChart(canvas, labels, realData, fakeData) {
        new Chart(canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Real News',
                        data: realData,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.15)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Fake News',
                        data: fakeData,
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.15)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#94a3b8' }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8', precision: 0 }
                    }
                }
            }
        });
    }

    function initPieChart(canvas, pieData) {
        new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: ['Real News', 'Fake News'],
                datasets: [{
                    data: pieData,
                    backgroundColor: ['#10b981', '#ef4444'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8', padding: 20 }
                    }
                }
            }
        });
    }
});
