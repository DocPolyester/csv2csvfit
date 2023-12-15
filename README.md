With the script you can transcode the WATERROWER/SMARTROW CSV to GARMIN CSV (FIT compliant format). 

usage:<br>

1.) first you will need to get the FitCSVTool from GARMIN

2.) ./csv2csvfit.py  -i 2023-12-13T180555_10000m.csv -o 2023-12-13T180555_10000m_FITREADY.csv

3.) java -jar FitCSVTool.jar -c 2023-12-13T180555_10000m_FITREADY.csv 2023-12-13T180555_10000m.fit 
