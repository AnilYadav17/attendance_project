// QR Scanning Logic
function onScanSuccess(decodedText, decodedResult) {
    // Handle the scanned code as you like, for example:
    console.log(`Code matched = ${decodedText}`, decodedResult);
    
    // Send to backend
    fetch('/api/mark-attendance/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ token: decodedText })
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('scan-result');
        resultDiv.innerText = data.message;
        
        if (data.status === 'success') {
            resultDiv.className = 'scan-result scan-success';
            // Stop scanning? html5QrcodeScanner.clear();
        } else {
            resultDiv.className = 'scan-result scan-error';
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function onScanFailure(error) {
    // handle scan failure, usually better to ignore and keep scanning.
    // console.warn(`Code scan error = ${error}`);
}

// Helper to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize Scanner if element exists
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('reader')) {
        let html5QrcodeScanner = new Html5QrcodeScanner(
            "reader",
            { 
                fps: 10, 
                qrbox: {width: 250, height: 250},
                supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA, Html5QrcodeScanType.SCAN_TYPE_FILE]
            },
            /* verbose= */ false);
        html5QrcodeScanner.render(onScanSuccess, onScanFailure);
    }
});
