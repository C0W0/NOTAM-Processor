# NOTAM Processor
### Disclaimer
**All data used in this project are from public sources and contain no confidential information. There is no guarantee of the accuracy of the predictions, and the projections should not be used for any purpose other than amateur "rocket-chasing."**
#### What is this project
This project uses publicly-available NOTAM information to train a neuron network model to prediction rocket launches.
#### What is a NOTAM
A Notice to Airmen is a notice filed with an aviation authority to alert aircraft pilots of potential hazards along a flight route or at a location that could affect the flight.
#### How are NOTAMs connected to rocket launches
Rocket launch activities create hazards to civil aviation flights, as ascending launch vehicles and falling debris pose a danger to nearby aircraft. This is why aviation authorities will close certain airspace during rocket launches. Air closures from aerospace activities have specific patterns, varying by the rocket and target orbit of the missions.
#### How are we doing this
This project aims to use these patterns to make predictions of the launch vehicle of aerospace activities by training a neuron network with historical NOTAM data. With some careful digging and some python scripts to fetch info from the FAA public database, we were able to get approximately 200 data points from the past two years. All data are from Chinese launches as of now.
