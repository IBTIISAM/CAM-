<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audio File Comparison</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body { padding: 20px; }
        audio { width: 200px; }
    </style>
</head>
<body>
    <h2>Compare Audio Files</h2>
    <!-- Form for submitting audio files -->
    <form id="databaseForm" enctype="multipart/form-data">
        <div class="form-group">
            <label for="audioFile">Upload Audio File:</label>
            <input type="file" class="form-control-file" id="audioFile" name="audioFile" required>
        </div>
        <div class="form-group">
            <label for="threshold">Score Threshold (%):</label>
            <input type="number" class="form-control" id="threshold" name="threshold" value="50" required>
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
    </form>

    <!-- Container for results -->
    <div id="databaseResult"></div>

    <!-- Button for downloading CSV -->
    <button id="download-csv" style="margin-top: 20px; display: none;" class="btn btn-success">Download Results as CSV</button>

    <!-- JavaScript libraries and scripts -->
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script>
        $(document).ready(function() {
            // Handle form submission
            $('#databaseForm').on('submit', function(e) {
                e.preventDefault(); // Prevent form submission
                var formData = new FormData(this);
                $.ajax({
                    type: 'POST',
                    url: '/compare_with_db',
                    data: formData,
                    cache: false,
                    contentType: false,
                    processData: false,
                    success: function(data) {
                        if (data.error) {
                            $('#databaseResult').html('<div class="alert alert-danger">' + data.error + '</div>');
                            $('#download-csv').hide();
                        } else {
                            let results = '<table class="table"><thead><tr><th>File</th><th>Score</th><th>Play</th></tr></thead><tbody>';
                            data.matches.forEach(match => {
                                let color = parseInt(match.score) >= parseInt($('#threshold').val()) ? 'text-success' : 'text-danger';
                                results += `<tr><td>${match.file}</td><td class="${color}">${match.score}%</td><td><button class="btn btn-info" onclick="playAudio('${match.file}')">Play</button></td></tr>`;
                            });
                            results += '</tbody></table>';
                            $('#databaseResult').html(results);
                            $('#download-csv').show();
                        }
                    },
                    error: function() {
                        $('#databaseResult').html('<div class="alert alert-danger">An error occurred while processing your request.</div>');
                        $('#download-csv').hide();
                    }
                });
            });

            // Function to handle audio playback
            window.playAudio = function(file) {
                const audioPlayer = new Audio(`./data/${file}`);
                audioPlayer.play()
                    .then(() => console.log('Playing ' + file))
                    .catch(error => console.error('Error playing the file:', error));
            };
            
            // Function to download results as CSV
            $('#download-csv').click(function() {
                let csvContent = "data:text/csv;charset=utf-8,";
                let rows = document.querySelectorAll('table tr');
                rows.forEach((row, index) => {
                    let cols = row.querySelectorAll('td, th');
                    let csvRow = [];
                    cols.forEach((col, i) => {
                        if (i !== 2) { // Skip the Play button column
                            csvRow.push('"' + col.innerText.replace(/"/g, '""') + '"');
                        }
                    });
                    csvContent += csvRow.join(",") + "\\n";
                });

                var encodedUri = encodeURI(csvContent);
                var link = document.createElement("a");
                link.setAttribute("href", encodedUri);
                link.setAttribute("download", "database_comparison_results.csv");
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            });
        });
    </script>
</body>
</html>