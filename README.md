# Stock Market Prediction & Portfolio Management Platform
**Stock Market Prediction** Web App based on **Machine Learning** and **Sentiment Analysis** of Tweets **(API keys included in code)**. The front end of the Web App is based on **Flask** and **Wordpress**. The App forecasts stock prices of the next seven days for any given stock under **NASDAQ** or **NSE** as input by the user. Predictions are made using three algorithms: **ARIMA, LSTM, Linear Regression**. The Web App combines the predicted prices of the next seven days with the **sentiment analysis of tweets** to give recommendation whether the price is going to rise or fall.

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#system-description-and-functions">System Description and Functions</a></li>
    <li><a href="#built-with">Built With</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#authors">Authors</a></li>
    <li><a href="#links">Links</a></li>
  </ol>
</details>

## Overview

A comprehensive stock market prediction and portfolio management platform that combines machine learning algorithms with sentiment analysis to provide investment insights and portfolio tracking capabilities.

## Screenshots

<img src="screenshots/banner.png">
<img src="screenshots/banner2.PNG">
<img src="screenshots/11-resuts.png" width="750">
<img src="screenshots/wp-admin.PNG" width="750">

**Default Admin Credentials:** <br/>
Username: admin <br/>
Password: admin123 <br/>
*Note: Change these credentials immediately after first login*

There are two roles in the system: **Admin** and **User**.<br/><br/>
Users can:<br/>
<ol>
    <li>Register and Login </li>
    <li>Check Real Time stock prices</li>
    <li>Read recent news about different stocks</li>
    <li>Currency Converter</li>
    <li>Edit or delete their own profile</li>
    <li>Educate the user about stocks</li>
    <li>Download list of stock tickers</li>
    <li>Predict Stock prices for the next 7 days for all NASDAQ and NSE stocks</li>
</ol>

Admin can:<br/>
<ol>
    <li>Create, Retrieve, Update Delete Users.</li>
    <li>Manually trigger emails.</li>
    <li>Register and Login </li>
    <li>Check Real Time stock prices</li>
    <li>Read recent news about different stocks</li>
    <li>Currency Converter</li>
    <li>Edit or delete their own profile</li>
    <li>Educate the user about stocks</li>
    <li>Download list of stock tickers</li>
    <li>Predict Stock prices for the next 7 days for all NASDAQ and NSE stocks</li>
</ol>

## Built With
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Javascript](https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E)
![django](https://img.shields.io/badge/Django-20232A?style=for-the-badge&logo=django&logoColor=white)
![nodejs](https://img.shields.io/badge/Node.js-43853D?style=for-the-badge&logo=node.js&logoColor=white)
![react](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![html](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![css](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)
![jquery](https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white)
![wordpress](https://img.shields.io/badge/Wordpress-006699?style=for-the-badge&logo=wordpress&logoColor=white)
![Keras](https://img.shields.io/badge/Keras-red?style=for-the-badge&logo=keras&logoColor=white)
![Numpy](https://img.shields.io/badge/Numpy-blue?style=for-the-badge&logo=numpy&logoColor=white)
![pandas](https://img.shields.io/badge/Pandas-green?style=for-the-badge&logo=pandas&logoColor=white)

## Installation
1. Install XAMPP server
2. Download wordpress zip folder from <a href="https://drive.google.com/file/d/1J753gY0Nv6HGSkPngSxrogNghDQnoIlk/view?usp=sharing">this link</a>.
3. Extract the downloaded zip into ```htdocs``` folder of XAMPP.
4. Open the ```wp-config.php``` file from the extracted folder and add your phpmyadmin username and password.
5. Go to phpmyadmin, create a new database called ```wordpress```.
6. Select this database, go to Operations tab and Import the ```wordpress.sql``` file into this created databse.
7. Clone the repo, cd into it
4. Run ```pip install -r requirements.txt```
5. Run ```python main.py``` to start server.
7. Go to ```localhost/wordpress``` to access the app.

Find more screenshots in the **screenshots** folder.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
