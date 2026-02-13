const temperature = document.getElementById("Temperature");
const humidity = document.getElementById("Humidity");

// Canvas contexts
const tempCtx = document.getElementById("tempChart").getContext("2d");
const humCtx = document.getElementById("humidityChart").getContext("2d");

const MAX_POINTS = 20;

// TEMPERATURE CHART
const tempChart = new Chart(tempCtx, {
    type: "line",
    data: {
        labels: [],
        datasets: [{
            label: "Temperature (°C)",
            data: [],
            borderWidth: 2,
            borderColor: "rgb(255,99,132)",
            backgroundColor: "rgba(255,99,132,0.2)",
            tension: 0.35
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                min: function(ctx) {
                    const data = ctx.chart.data.datasets[0].data;
                    if (!data.length) return 0;
                    return Math.min(...data) - 2;
                },
                max: function(ctx) {
                    const data = ctx.chart.data.datasets[0].data;
                    if (!data.length) return 50;
                    return Math.max(...data) + 2;
                },
                ticks: {
                    maxTicksLimit: 7,
                    color: "white"
                }
            },
            x: {
                display: false
            }
        },
        plugins: {
            legend: {
                labels: {
                    color: "white"
                }
            }
        }
    }
});

// HUMIDITY CHART
const humChart = new Chart(humCtx, {
    type: "line",
    data: {
        labels: [],
        datasets: [{
            label: "Humidity (%)",
            data: [],
            borderWidth: 2,
            borderColor: "rgb(54,162,235)",
            backgroundColor: "rgba(54,162,235,0.2)",
            tension: 0.35
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        scales: {
            y: {
                min: function(ctx) {
                    const data = ctx.chart.data.datasets[0].data;
                    if (!data.length) return 0;
                    return Math.min(...data) - 5;
                },
                max: function(ctx) {
                    const data = ctx.chart.data.datasets[0].data;
                    if (!data.length) return 100;
                    return Math.max(...data) + 5;
                },
                ticks: {
                    maxTicksLimit: 7,
                    color: "white"
                }
            },
            x: {
                display: false
            }
        },
        plugins: {
            legend: {
                labels: {
                    color: "white"
                }
            }
        }
    }
});

// UPDATE FUNCTION
async function fetchSensorData() {
    try {
        const response = await fetch("api/sensor/latest");
        const data = await response.json();

        if (data.temperature !== undefined) {
            
            temperature.textContent = data.temperature.toFixed(2);
            humidity.textContent = data.humidity.toFixed(2);

            const label = new Date().toLocaleTimeString();

            // Update temperature chart
            tempChart.data.labels.push(label);
            tempChart.data.datasets[0].data.push(data.temperature);
            if (tempChart.data.labels.length > MAX_POINTS) {
                tempChart.data.labels.shift();
                tempChart.data.datasets[0].data.shift();
            }
            tempChart.update();

            // Update humidity chart
            humChart.data.labels.push(label);
            humChart.data.datasets[0].data.push(data.humidity);
            if (humChart.data.labels.length > MAX_POINTS) {
                humChart.data.labels.shift();
                humChart.data.datasets[0].data.shift();
            }
            humChart.update();
        }
    } catch (error) {
        console.error("Error fetching sensor data:", error);
    }
}

fetchSensorData();

// Update every 2 seconds
setInterval(fetchSensorData, 2000);