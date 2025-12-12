// Main JS
document.addEventListener('DOMContentLoaded', function() {
    console.log('Attendance System Loaded');
    
    // Auto-hide alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    });
});
