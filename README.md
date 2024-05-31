# Audio Comparison Application

## Quickstart

### Run the Application

To run the application, execute the following command in your terminal:

sh
./start.sh

### Description of the Application

Once the application is running, navigate to http://localhost:5000 in your web browser. This will take you to the main page, which provides two primary options:

1. Compare Two Files
Clicking on "Compare Two Files" will take you to a page where you can compare two audio files. You have the option to either upload an audio file or record a new one directly on the page.

Upload or Record Audio: Select an audio file to upload or use the record functionality to record new audio.
Set Threshold: Adjust the threshold to determine whether the two audio files are considered a match.
Submit: Click the "Submit" button to compare the audio files. The result will indicate whether the files match based on the set threshold.
Back to Main Page: Click the "Back" button in the top left corner to return to the main page.

2. Compare with Database
Clicking on "Compare with Database" will take you to a page where you can upload an audio file to be compared against a database of audio files.

Upload Audio File: Select an audio file to upload for comparison.
Set Threshold: Adjust the threshold to determine the similarity score required for a match.
Submit: Click the "Submit" button to compare the uploaded audio file with the database.
View Results: Files that exceed the threshold will be displayed in a table with their file names and similarity scores.
Download CSV: You can download the results as a CSV file by clicking the "Download CSV File" button located at the bottom left corner below the table.
Back to Main Page: Click the "Back" button in the top left corner to return to the main page.

## Additional Information
Audio Formats: The application supports various audio formats for uploading and recording.
Threshold Setting: The threshold is a numeric value that determines the sensitivity of the comparison. A lower threshold might yield more matches, while a higher threshold will be more stringent.

CSV Download: The CSV file contains the list of files from the database that matched the uploaded audio file, along with their respective similarity scores.

