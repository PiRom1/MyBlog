// HP Timeline Chart
const hpData = hpTimelineData;
const hpCtx = document.getElementById('hpChart').getContext('2d');

// color palettes for timeline charts
const blueShades = ['rgba(54, 235, 235, 1)', 'rgba(0, 128, 255, 1)', 'rgba(73, 10, 200, 1)'];
const redOrangeShades = ['rgba(255, 127, 30, 1)', 'rgba(255, 72, 0, 1)', 'rgba(169, 0, 31, 1)'];

new Chart(hpCtx, {
    type: 'line',
    data: {
        datasets: Object.entries(hpData).map(([dino, data], idx, arr) => {
            // prefer first 3 as blue, last 3 as red/orange; fallback by modulo
            const color = idx < 3 ? blueShades[idx % blueShades.length] : redOrangeShades[(idx - 3) % redOrangeShades.length];
            return {
                label: dino,
                data: data.map(([tick, hp]) => ({x: tick/100, y: hp})),
                borderColor: color,
                backgroundColor: color.replace(/1\)$/, '0.1)'),
                borderWidth: 2,
                tension: 0.1,
                fill: false
            };
        })
    },
    options: {
        responsive: true,
        scales: {
            x: {
                type: 'linear',
                title: {
                    display: true,
                    text: 'Time (seconds)'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'HP'
                },
                beginAtZero: true
            }
        }
    }
});

// Damage Timeline Chart
const damageTimelineData = dinoTimelineData;
const damageTimelineCtx = document.getElementById('damageTimelineChart').getContext('2d');

new Chart(damageTimelineCtx, {
    type: 'line',
    data: {
        datasets: Object.entries(damageTimelineData).map(([dino, data], idx) => {
            const color = idx < 3 ? blueShades[idx % blueShades.length] : redOrangeShades[(idx - 3) % redOrangeShades.length];
            return {
                label: dino,
                data: data.map(([tick, damage]) => ({x: tick/100, y: damage})),
                borderColor: color,
                backgroundColor: color.replace(/1\)$/, '0.1)'),
                borderWidth: 2,
                tension: 0.1,
                fill: false
            };
        })
    },
    options: {
        responsive: true,
        scales: {
            x: {
                type: 'linear',
                title: {
                    display: true,
                    text: 'Time (seconds)'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Cumulative Damage'
                },
                beginAtZero: true
            }
        }
    }
});

// Damage Distribution Chart
const damageData = damageDealtData;
const damageCtx = document.getElementById('damageChart').getContext('2d');

new Chart(damageCtx, {
    type: 'bar',
    data: {
        labels: Object.keys(damageData),
        datasets: [
            {
                label: 'Attack Damage',
                data: Object.values(damageData).map(d => d.total),
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                stack: 'Stack 0'
            },
            {
                label: 'Reflect Damage',
                data: Object.values(damageData).map(d => d.reflect_damage || 0),
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                stack: 'Stack 0'
            },
            {
                label: 'Poison Damage',
                data: Object.values(damageData).map(d => d.poison_damage || 0),
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
                stack: 'Stack 0'
            },
            {
                label: 'Ability Damage',
                data: Object.values(damageData).map(d => d.ability_damage || 0),
                backgroundColor: 'rgba(153, 102, 255, 0.5)',
                stack: 'Stack 0'
            },
            {
                label: 'Execute Damage',
                data: Object.values(damageData).map(d => d.execute_damage || 0),
                backgroundColor: 'rgba(255, 159, 64, 0.5)',
                stack: 'Stack 0'
            },
            {
                label: 'Healing Done',
                data: Object.values(damageData).map(d => d.healing_done || 0),
                backgroundColor: 'rgba(76, 175, 80, 0.5)',
                stack: 'Stack 1'
            }
        ]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Damage / Healing'
                },
                stacked: true
            },
            x: {
                stacked: true
            }
        }
    }
});
