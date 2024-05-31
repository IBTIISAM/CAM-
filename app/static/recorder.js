document.addEventListener('DOMContentLoaded', () => {

    // Setup for Voice 1 and Voice 2
    let recordedBlobsVoice1 = [];
    let recordedBlobsVoice2 = [];
    let uploadedFileVoice1 = null;
    let uploadedFileVoice2 = null;

    setupVoiceControls('1', recordedBlobsVoice1, (file) => uploadedFileVoice1 = file);
    setupVoiceControls('2', recordedBlobsVoice2, (file) => uploadedFileVoice2 = file);

    // Submit button event listener
    document.getElementById('submitVoices').addEventListener('click', () => {
        const thresholdValue = document.getElementById('threshold').value;  // Fetch the threshold value

        const formData = new FormData();

        // Determine the blobs to use for comparison
        if (uploadedFileVoice1) {
            formData.append('voice1', uploadedFileVoice1, uploadedFileVoice1.name);  // Keep original name
        } else {
            const voice1Blob = new Blob(recordedBlobsVoice1, {type: 'audio/webm'});
            formData.append('voice1', voice1Blob, 'voice1.webm');  // Use fixed name for recorded audio
        }

        if (uploadedFileVoice2) {
            formData.append('voice2', uploadedFileVoice2, uploadedFileVoice2.name);  // Keep original name
        } else {
            const voice2Blob = new Blob(recordedBlobsVoice2, {type: 'audio/webm'});
            formData.append('voice2', voice2Blob, 'voice2.webm');  // Use fixed name for recorded audio
        }

        formData.append('threshold', thresholdValue);  // Append threshold to FormData

        fetch('/compare_two', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            // Handle success - Update the UI with the comparison result
            const resultText = document.getElementById('comparisonResult');
            const isMatch = data.confidence >= thresholdValue;
            resultText.textContent = isMatch ? `It's a match (${data.confidence}%)` : `Not a match (${data.confidence}%)`;
            resultText.style.color = isMatch ? '#28a745' : '#dc3545'; // Green for match, red for not a match
        })
        .catch(error => {
            console.error('Error:', error);
            
        });
    });

    function setupVoiceControls(voiceNumber, recordedBlobs, setUploadedFileCallback) {
        const recordButton = document.getElementById('recordButton' + voiceNumber);
        const audioPlayback = document.getElementById('audioPlayback' + voiceNumber);
        const statusText = document.getElementById('status' + voiceNumber);
        const audioUpload = document.getElementById('audioUpload' + voiceNumber);

        let mediaRecorder = null;
        let activeStream = null;

        // Toggle recording
        recordButton.addEventListener('click', () => toggleRecording());

        // Upload audio file
        audioUpload.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                setUploadedFileCallback(file);
                audioPlayback.src = URL.createObjectURL(file);
                audioPlayback.hidden = false;
                statusText.textContent = 'Uploaded file for Voice ' + voiceNumber + '.';
                recordedBlobs.length = 0; // Clear recorded blobs as we have an uploaded file now
            }
        });

        function toggleRecording() {
            if (recordButton.textContent === `Start Recording Voice ${voiceNumber}`) {
                startRecording();
            } else {
                stopRecording();
            }
        }

        function startRecording() {
            navigator.mediaDevices.getUserMedia({ audio: true, video: false })
                .then(stream => {
                    mediaRecorder = new MediaRecorder(stream);
                    activeStream = stream;

                    mediaRecorder.ondataavailable = event => {
                        if (event.data.size > 0) {
                            recordedBlobs.push(event.data);
                        }
                    };

                    mediaRecorder.start();
                    recordButton.textContent = `Stop Recording Voice ${voiceNumber}`;
                    statusText.textContent = `Recording Voice ${voiceNumber}... Click the button again to stop.`;
                })
                .catch(error => {
                    console.error('Error accessing media devices:', error);
                    statusText.textContent = 'Failed to access media devices. Check console for errors.';
                });
        }

        function stopRecording() {
            if (mediaRecorder) {
                mediaRecorder.stop();
                mediaRecorder.onstop = () => {
                    const blob = new Blob(recordedBlobs, {type: 'audio/webm'});
                    audioPlayback.src = URL.createObjectURL(blob);
                    audioPlayback.hidden = false;
                    recordButton.textContent = `Start Recording Voice ${voiceNumber}`;

                    statusText.textContent = `Recording stopped. Play the audio or record again for Voice ${voiceNumber}.`;
                };

                if (activeStream) {
                    activeStream.getTracks().forEach(track => track.stop());
                    activeStream = null;
                }
            }
        }
    }
});