# AutomationProject

Connecting Multiple APIs to accomplish tasks
Goal: Keep Track of different restaurants and places that I have gone 
      (Easy to update using SMS)
      Keep track of different kinds of beer that I have tried
      (Easy to update using SMS or barcode scan)

Resturant flow diagram
1)SMS message (Twillio)
2)Recognize text format to be resturant name (regex)
3)Query yelp API with resurant name
  (Returns coordinates and price)
4)Updates SQL database with the information 
5) SMS message to confirm success
 
Part 2
6) Go to python server and query the SQL database by location
7) Using google maps API show all places where I have eaten 
 
Beer Flow Diagram
1)SMS message (Twillio) 
OR 
Upload photo to barcode to website
Using (openCV and pyzbar and webscraping) 
2)Recognize text format to be resturant name (regex)
3)Webscrapping
  (Returns beer type and manufacturer)
4)Updates SQL database with the information 
5) SMS message to confirm success

Part 2
6) Go to python server and query the SQL database
7) Returns beer names and ratings
 
