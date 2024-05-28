document.addEventListener('DOMContentLoaded', function() {
    setupFormSubmissions();
});

function setupFormSubmissions() {
    const compareForm = document.getElementById('compareForm');
    const databaseForm = document.getElementById('databaseForm');

    compareForm.addEventListener('submit', function(e) {
        e.preventDefault();
        handleFormSubmit(this, '/compare_two', 'compareResult');
    });

    databaseForm.addEventListener('submit', function(e) {
        e.preventDefault();
        handleFormSubmit(this, '/compare_with_db', 'databaseResult');
    });
}

async function handleFormSubmit(form, url, resultContainerId) {
    const formData = new FormData(form);
    showLoadingIndicator(resultContainerId);

    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        updateResult(data, resultContainerId);
    } catch (error) {
        console.error('Fetch error:', error);
        document.getElementById(resultContainerId).innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
}

function updateResult(data, resultContainerId) {
    const resultContainer = document.getElementById(resultContainerId);

    if (!data) {
        console.error("Received null or undefined data.");
        resultContainer.innerHTML = '<div class="alert alert-danger">No data received.</div>';
        return;
    }

    let results = '';
    if (resultContainerId === 'compareResult') {
        let matchStatus = data.match ? 'Match' : 'No Match';
        let alertClass = data.match ? 'alert-success' : 'alert-danger';
        results = `<div class="alert ${alertClass}">${matchStatus}</div>`;
    } else if (resultContainerId === 'databaseResult') {
        results = '<table class="table"><thead><tr><th>File</th><th>Score</th><th>Play</th></tr></thead><tbody>';
        data.matches.forEach(match => {
            let audioPath = `./data/${match.file}`;
            results += `<tr><td>${match.file}</td><td>${match.score}%</td><td><audio controls src="${audioPath}"></audio></td></tr>`;
        });
        results += '</tbody></table>';
    }

    resultContainer.innerHTML = results;
}

function showLoadingIndicator(resultContainerId) {
    const resultContainer = document.getElementById(resultContainerId);
    resultContainer.innerHTML = '<div class="loading">Loading...</div>';
}