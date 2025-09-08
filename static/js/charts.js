// Chart.js global configuration and utilities
document.addEventListener('DOMContentLoaded', function() {
    // Global Chart.js defaults
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
        Chart.defaults.font.size = 12;
        Chart.defaults.color = '#666';
        Chart.defaults.plugins.legend.position = 'top';
        Chart.defaults.plugins.legend.align = 'center';
        Chart.defaults.scales.linear.grid.color = 'rgba(0, 0, 0, 0.1)';
        Chart.defaults.scales.linear.ticks.color = '#666';
        Chart.defaults.maintainAspectRatio = false;
    }
});