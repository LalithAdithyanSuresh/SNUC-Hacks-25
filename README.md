# DIY-Namo -> AI based DIY Project recommendation
## Team Name: 0xBY7E 
## Team Members  
- **Lalith Adithyan S**
- **Lithikha B**  
- **Sanjeev Krishna** 
- **Anjana K** 

---

## Overview  
This project integrates AI-powered DIY experiment generation with a web-based system that provides fun, safe, and interactive experiments based on real-world detected objects.  

- Uses Google Gemini AI to generate fun, safe DIY experiments based on object detection data.  
- Filters outliers using Z-score statistical methods to remove irrelevant object detections.  
- Provides experiment-specific object descriptions instead of generic ones.  
- Stores user sessions and experiment history in a MySQL database.  
- Flask API and PHP-based web interface for seamless interaction.  

---

## Features  
- AI-powered DIY experiment generation using Gemini AI.  
- Statistical outlier removal for more accurate experiment suggestions.  
- Object-specific descriptions related to each experiment.  
- MySQL database for session management and data storage.  
- Flask API with CORS for smooth front-end and back-end communication.  
- PHP-based website for user-friendly interaction.  

---

## Project Architecture  

### 1. Object Detection & Filtering  
- Objects are detected and counted.  
- Z-score method is applied to filter outliers.  

### 2. AI Experiment Generation  
- Filtered object list is sent to Google Gemini AI.  
- AI returns three structured DIY experiments in JSON format.  
- Object-specific descriptions are generated.  

### 3. Web Interface & API  
- Flask API handles requests and responses.  
- PHP-based website displays experiments to users.  
- Users can browse experiments based on detected objects.  
- MySQL database stores user sessions and experiment history.  

---

## Tech Stack  
- **Backend:** Python (Flask), Google Gemini AI, NumPy  
- **Frontend:** HTML, CSS, JavaScript (PHP for dynamic content)  
- **Database:** MySQL  
- **APIs:** Flask REST API  

---

## Installation & Setup  

### 1. Clone the Repository  
```bash
git clone https://github.com/your-repo/diy-experiment-generator.git
cd diy-experiment-generator
```
### 2. Install Dependencies
```bash
pip install google-generativeai flask flask-cors numpy mysql-connector-python
```
###  3. Set Up API Key
```bash
API_KEY = "your_gemini_api_key"
```

# How It Works  

- Objects are detected (manual input or automated detection).  
- Outliers are removed using Z-score filtering.  
- Filtered objects are sent to Gemini AI.  
- AI returns three DIY experiments in JSON format.  
- Web interface (PHP + HTML) displays experiments to users.  
- Users interact with experiment descriptions based on detected objects.  

---

# Future Enhancements  

- Add real-time object detection (e.g., via OpenCV).  
- Improve experiment recommendation using machine learning models.  
- Integrate a community sharing feature for user-generated experiments.  
