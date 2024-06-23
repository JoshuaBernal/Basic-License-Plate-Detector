## License Plate Detection and Recognition Application
------------------------------------------
This is a small-scale Automatic License Plate Reader (ALPR) created as a desktop application using yOLOv8 and easyOCR.

#### Get the pre-trained model <a href="https://github.com/AarohiSingla/Automatic-Number-Plate-Recognition--ANPR-.git">here</a>.

#### Download the ZIP file on the latest release to get the desktop application.

#### To compile the desktop application yourself, follow the steps below:
1. Open your terminal and navigate to the desktop-app folder.
2. Run the command `pyinstaller --onefile -w LicensePlateReader.py`
3. After compiling is finished, copy the contents of `./spec-file.txt` to `/desktop-app/LicensePlateReader.spec`.
4. Run the command `pyinstaller LicensePlateReader.spec`
5. Delete the `/desktop-app/dist/LicensePlateReader.exe` file, the one with the Python app icon.
6. You can find the app on `/desktop-app/dist/License Plate Reader.exe`. It is the one with the orange car icon.
