// Global chart objects
let revenueChart, categoryChart, regionChart;
let map = null; // To store the map instance
let selectedRegion = 'all'; // Default to all regions

// Format numbers for display
function formatCurrency(value) {
    return '$' + value.toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });
}

function formatNumber(value) {
    return value.toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });
}

// Create Geo Distribution Map
function createGeoMap() {
    fetch('/api/state_growth_data?region=' + selectedRegion)
        .then(response => response.json())
        .then(data => {
            // Initialize the map if it doesn't exist
            if (!map) {
                map = L.map('mapChart').setView([37.8, -96], 4); // Center on US
                
                // Add tile layer (base map)
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                    maxZoom: 18
                }).addTo(map);
            } else {
                // Clear existing layers if map already exists
                map.eachLayer(function(layer) {
                    if (layer instanceof L.Circle) {
                        map.removeLayer(layer);
                    }
                });
            }
            
            // US state coordinates (approximate centers)
            const stateCoordinates = {
                "Alabama": [32.806671, -86.791130],
                "Alaska": [61.370716, -152.404419],
                "Arizona": [33.729759, -111.431221],
                "Arkansas": [34.969704, -92.373123],
                "California": [36.116203, -119.681564],
                "Colorado": [39.059811, -105.311104],
                "Connecticut": [41.597782, -72.755371],
                "Delaware": [39.318523, -75.507141],
                "Florida": [27.766279, -81.686783],
                "Georgia": [33.040619, -83.643074],
                "Hawaii": [21.094318, -157.498337],
                "Idaho": [44.240459, -114.478828],
                "Illinois": [40.349457, -88.986137],
                "Indiana": [39.849426, -86.258278],
                "Iowa": [42.011539, -93.210526],
                "Kansas": [38.526600, -96.726486],
                "Kentucky": [37.668140, -84.670067],
                "Louisiana": [31.169546, -91.867805],
                "Maine": [44.693947, -69.381927],
                "Maryland": [39.063946, -76.802101],
                "Massachusetts": [42.230171, -71.530106],
                "Michigan": [43.326618, -84.536095],
                "Minnesota": [45.694454, -93.900192],
                "Mississippi": [32.741646, -89.678696],
                "Missouri": [38.456085, -92.288368],
                "Montana": [46.921925, -110.454353],
                "Nebraska": [41.125370, -98.268082],
                "Nevada": [38.313515, -117.055374],
                "New Hampshire": [43.452492, -71.563896],
                "New Jersey": [40.298904, -74.521011],
                "New Mexico": [34.840515, -106.248482],
                "New York": [42.165726, -74.948051],
                "North Carolina": [35.630066, -79.806419],
                "North Dakota": [47.528912, -99.784012],
                "Ohio": [40.388783, -82.764915],
                "Oklahoma": [35.565342, -96.928917],
                "Oregon": [44.572021, -122.070938],
                "Pennsylvania": [40.590752, -77.209755],
                "Rhode Island": [41.680893, -71.511780],
                "South Carolina": [33.856892, -80.945007],
                "South Dakota": [44.299782, -99.438828],
                "Tennessee": [35.747845, -86.692345],
                "Texas": [31.054487, -97.563461],
                "Utah": [40.150032, -111.862434],
                "Vermont": [44.045876, -72.710686],
                "Virginia": [37.769337, -78.169968],
                "Washington": [47.400902, -121.490494],
                "West Virginia": [38.491226, -80.954453],
                "Wisconsin": [44.268543, -89.616508],
                "Wyoming": [42.755966, -107.302490]
            };
            
            // Find max revenue for scaling
            let maxRevenue = 0;
            Object.keys(data).forEach(region => {
                data[region].revenue.forEach(rev => {
                    if (rev > maxRevenue) maxRevenue = rev;
                });
            });
            
            // Function to determine color based on growth rate
            function getGrowthColor(growth) {
                if (growth <= -10) return '#d7191c'; // Dark red for significant decline
                if (growth < 0) return '#fdae61';    // Light orange for moderate decline
                if (growth < 5) return '#ffffbf';    // Yellow for minimal growth
                if (growth < 15) return '#a6d96a';   // Light green for moderate growth
                return '#1a9641';                    // Dark green for significant growth
            }
            
            // Add legend to show growth color meanings
            if (!map.legend) {
                const legend = L.control({ position: 'bottomright' });
                legend.onAdd = function() {
                    const div = L.DomUtil.create('div', 'info legend');
                    div.style.backgroundColor = 'rgba(0, 47, 95, 0.9)';
                    div.style.padding = '6px';
                    div.style.borderRadius = '5px';
                    div.style.boxShadow = '0 0 15px rgba(0,0,0,0.2)';
                    div.style.color = 'white';
                    div.style.border = '1px solid #0059b3';
                    
                    div.innerHTML = '<div style="font-weight:bold;margin-bottom:5px;">Growth %</div>';
                    
                    const grades = [15, 5, 0, -10, -20];
                    const labels = ['> 15%', '5-15%', '0-5%', '-10-0%', '< -10%'];
                    const colors = ['#1a9641', '#a6d96a', '#ffffbf', '#fdae61', '#d7191c'];
                    
                    for (let i = 0; i < grades.length; i++) {
                        div.innerHTML +=
                            '<div style="display:flex;align-items:center;margin:3px 0;"><i style="background:' + colors[i] + ';width:18px;height:18px;margin-right:8px;border-radius:50%;display:inline-block;"></i> ' +
                            labels[i] + '</div>';
                    }
                    
                    return div;
                };
                legend.addTo(map);
                map.legend = legend;
            }
            
            // Add bubbles for each state
            Object.keys(data).forEach(region => {
                const regionData = data[region];
                
                for (let i = 0; i < regionData.states.length; i++) {
                    const state = regionData.states[i];
                    const revenue = regionData.revenue[i];
                    const growth = regionData.growth[i];
                    
                    if (stateCoordinates[state]) {
                        // Scale bubble size based on revenue (sqrt for area proportionality)
                        const radius = Math.sqrt(revenue / maxRevenue) * 50000;
                        
                        // Color based on growth rate
                        const color = getGrowthColor(growth);
                        
                        // Create bubble
                        L.circle(stateCoordinates[state], {
                            color: color,
                            fillColor: color,
                            fillOpacity: 0.6,
                            radius: radius
                        }).addTo(map)
                        .bindPopup(`<div style="color: #003366;"><strong>${state}</strong><br>Region: ${region}<br>Revenue: ${formatCurrency(revenue)}<br>Growth: ${growth.toFixed(1)}%</div>`);
                    }
                }
            });
        })
        .catch(error => console.error('Error creating geo map:', error));
}

// Fetch KPI data
function fetchKPIData() {
    fetch('/api/kpi_data?region=' + selectedRegion)
        .then(response => response.json())
        .then(data => {
            document.getElementById('totalRevenue').textContent = formatCurrency(data.total_revenue);
            document.getElementById('totalProfit').textContent = formatCurrency(data.total_profit);
            document.getElementById('regionsCount').textContent = data.regions_count;
            document.getElementById('unitsSold').textContent = formatNumber(data.total_units);
        })
        .catch(error => console.error('Error fetching KPI data:', error));
}

// Create Revenue Over Time Chart
function createRevenueChart() {
    fetch('/api/revenue_over_time?region=' + selectedRegion)
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('revenueChart').getContext('2d');
            
            if (revenueChart) {
                revenueChart.destroy();
            }
            
            revenueChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.dates,
                    datasets: [
                        {
                            label: 'Revenue',
                            data: data.revenue,
                            borderColor: 'rgba(54, 162, 235, 1)',
                            backgroundColor: 'rgba(54, 162, 235, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.3
                        },
                        {
                            label: 'Profit',
                            data: data.profit,
                            borderColor: 'rgba(75, 192, 192, 1)',
                            backgroundColor: 'rgba(75, 192, 192, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                color: 'white'
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.dataset.label + ': ' + formatCurrency(context.raw);
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return formatCurrency(value);
                                },
                                color: 'white'
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        },
                        x: {
                            ticks: {
                                color: 'white'
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error creating revenue chart:', error));
}

// Create Category Donut Chart
function createCategoryChart() {
    fetch('/api/revenue_by_category?region=' + selectedRegion)
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('categoryChart').getContext('2d');
            
            // Define colors for categories
            const backgroundColors = [
                'rgba(255, 99, 132, 0.7)',
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 206, 86, 0.7)',
                'rgba(75, 192, 192, 0.7)',
                'rgba(153, 102, 255, 0.7)',
                'rgba(255, 159, 64, 0.7)'
            ];
            
            if (categoryChart) {
                categoryChart.destroy();
            }
            
            categoryChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.categories,
                    datasets: [{
                        data: data.revenue,
                        backgroundColor: backgroundColors,
                        borderColor: 'white',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                boxWidth: 12,
                                font: {
                                    size: 11
                                },
                                color: 'white'
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const value = context.raw;
                                    const percentage = Math.round((value / total) * 100);
                                    return context.label + ': ' + formatCurrency(value) + ' (' + percentage + '%)';
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error creating category chart:', error));
}

// Create Region Bar Chart
function createRegionChart() {
    fetch('/api/revenue_by_region?region=' + selectedRegion)
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('regionChart').getContext('2d');
            
            // Define colors for regions with highlighting for selected region
            const backgroundColors = data.regions.map(region => {
                if (selectedRegion !== 'all' && region === selectedRegion) {
                    return 'rgba(255, 215, 0, 0.9)'; // Gold for selected region
                }
                return 'rgba(54, 162, 235, 0.7)';
            });
            
            if (regionChart) {
                regionChart.destroy();
            }
            
            regionChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.regions,
                    datasets: [{
                        label: 'Revenue by Region',
                        data: data.revenue,
                        backgroundColor: backgroundColors,
                        borderColor: 'rgba(0, 0, 0, 0.1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return 'Revenue: ' + formatCurrency(context.raw);
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    if (value >= 1000) {
                                        return '$' + value / 1000 + 'k';
                                    }
                                    return '$' + value;
                                },
                                color: 'white'
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        },
                        y: {
                            ticks: {
                                color: 'white'
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        }
                    }
                }
            });
            
            // Populate region filter
            const regionFilter = document.getElementById('regionFilter');
            // Only repopulate if the filter is empty (except for 'all')
            if (regionFilter.options.length <= 1) {
                // Add options for each region
                data.regions.forEach(region => {
                    const option = document.createElement('option');
                    option.value = region;
                    option.textContent = region;
                    regionFilter.appendChild(option);
                });
            }
        })
        .catch(error => console.error('Error creating region chart:', error));
}

// Fetch and display growing categories
function fetchGrowingCategories() {
    fetch('/api/growth_by_category?region=' + selectedRegion)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('growingCategories');
            container.innerHTML = '';
            
            for (let i = 0; i < data.categories.length; i++) {
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center';
                
                const category = document.createElement('span');
                category.textContent = data.categories[i];
                
                const growth = document.createElement('span');
                growth.className = 'badge bg-success rounded-pill';
                growth.textContent = '+' + data.growth[i].toFixed(1) + '%';
                
                li.appendChild(category);
                li.appendChild(growth);
                container.appendChild(li);
            }
        })
        .catch(error => console.error('Error fetching growing categories:', error));
}

// Fetch and display outperforming regions
function fetchOutperformingRegions() {
    fetch('/api/outperforming_regions?region=' + selectedRegion)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('outperformingRegions');
            container.innerHTML = '';
            
            for (let i = 0; i < data.regions.length; i++) {
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center';
                
                const region = document.createElement('span');
                region.textContent = data.regions[i];
                
                const revenue = document.createElement('span');
                revenue.className = 'text-success fw-bold';
                revenue.textContent = formatCurrency(data.revenue[i]);
                
                li.appendChild(region);
                li.appendChild(revenue);
                container.appendChild(li);
            }
        })
        .catch(error => console.error('Error fetching outperforming regions:', error));
}

// Event listeners for filters
document.getElementById('yearFilter').addEventListener('change', function() {
    // In a real application, we would re-fetch data based on the selected year
    // For now, we'll just reload the existing charts
    loadAllData();
    
    // Resize map after filter change (to fix rendering issues)
    setTimeout(function() {
        if (map) map.invalidateSize();
    }, 100);
});

document.getElementById('regionFilter').addEventListener('change', function() {
    // Get the selected region
    selectedRegion = this.value;
    
    // Update page title to show selected region
    updateDashboardTitle(selectedRegion);
    
    // Reload all data with the new region filter
    loadAllData();
    
    // Resize map after filter change (to fix rendering issues)
    setTimeout(function() {
        if (map) map.invalidateSize();
    }, 100);
});

// Update dashboard title based on selected region
function updateDashboardTitle(region) {
    const titleElement = document.querySelector('header h1');
    const defaultTitle = "Retail Analytics Strategic Dashboard";
    const regionFilter = document.getElementById('regionFilter');
    
    // Reset any previous styling
    regionFilter.classList.remove('region-filter-active');
    
    if (region === 'all') {
        titleElement.textContent = defaultTitle;
    } else {
        // Add highlighting to the title with the region name
        titleElement.innerHTML = `<span class="region-highlight">${region}</span> Region - Strategic Dashboard`;
        
        // Add active filter indicator
        regionFilter.classList.add('region-filter-active');
    }
}

// Load all data
function loadAllData() {
    fetchKPIData();
    createRevenueChart();
    createCategoryChart();
    createRegionChart();
    createGeoMap();
    fetchGrowingCategories();
    fetchOutperformingRegions();
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadAllData();
    
    // Handle window resize events
    window.addEventListener('resize', function() {
        if (map) map.invalidateSize();
    });
    
    // Handle tab visibility changes
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible' && map) {
            setTimeout(function() {
                map.invalidateSize();
            }, 200);
        }
    });
}); 