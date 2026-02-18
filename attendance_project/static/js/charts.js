// Charts Logic
document.addEventListener('DOMContentLoaded', function() {
    // Attendance Chart
    const ctx = document.getElementById('attendanceChart');
    if (ctx) {
        // Get data from template
        const labels = JSON.parse(document.getElementById('chart-labels').textContent);
        const data = JSON.parse(document.getElementById('chart-data').textContent);

        // Create gradient
        const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(0, 242, 254, 0.4)'); // Neon Cyan
        gradient.addColorStop(1, 'rgba(0, 242, 254, 0.05)');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Classes Attended',
                    data: data,
                    borderColor: '#00f2fe', // Neon Cyan
                    backgroundColor: gradient,
                    borderWidth: 3,
                    pointBackgroundColor: '#0f172a', // Dark Bg
                    pointBorderColor: '#00f2fe',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(30, 41, 59, 0.95)', // Slate 800
                        titleColor: '#f1f5f9', // Slate 100
                        bodyColor: '#00f2fe', // Neon Cyan
                        borderColor: '#334155', // Slate 700
                        borderWidth: 1,
                        padding: 12,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return context.parsed.y + ' Classes';
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#334155', // Slate 700
                            borderDash: [5, 5]
                        },
                        ticks: {
                            stepSize: 1,
                            color: '#94a3b8', // Slate 400
                            font: {
                                family: "'Inter', sans-serif",
                                size: 11
                            }
                        },
                        border: {
                            display: false
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#94a3b8', // Slate 400
                            font: {
                                family: "'Inter', sans-serif",
                                size: 12
                            }
                        },
                        border: {
                            display: false
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }
});
