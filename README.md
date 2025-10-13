# 🧠 Lead Scoring Web App (AI-Powered)

This tool is an **AI-based Lead Scoring System** built using **Streamlit** and **Logistic Regression**.  
It predicts lead conversion likelihood (Lead Score) and provides **visual insights** using histograms and feature importance charts.

---

## 🚀 Features

✅ Upload any `.csv` file with lead data  
✅ Automatically detects numeric or text-based fields  
✅ Generates lead conversion probability (Lead Score %)  
✅ Interactive data table and downloadable results  
✅ Feature importance visualization using Logistic Regression  
✅ Filter, sort, and summarize leads directly in the web UI  

---

## 🧩 Project Structure

<img width="589" height="348" alt="image" src="https://github.com/user-attachments/assets/03252999-586f-4ab5-9244-10ddaf1c4ba6" />


---

## ⚙️ Installation & Setup

Follow these steps to run the project locally 👇

### 1️⃣ Clone the repository ->
#'''bash
git clone https://github.com/Rupeshbhardwaj002/LeadGen_AI_Enhancer

### 2️⃣ Create and activate a virtual environment-> 
#### For Windows: ->

'''bash

python -m venv venv

venv\Scripts\activate

#### For Mac/Linux: ->
'''bash

python3 -m venv venv

source venv/bin/activate

### 3️⃣ Install dependencies: ->
'''bash

pip install -r requirements.txt


## 🧠 Run the App->

Run the Streamlit server locally:

'''bash

streamlit run app.py

Once started, open the link shown in your terminal (typically http://localhost:8501) �

## 🧮 Example Output: ->
After uploading your dataset:

A Lead Score Table will appear

You can download the scored leads as CSV

Visuals will show:

Lead Score Distribution

Logistic Regression Feature Importance

Tech Stack>
Component	Technology Used
Frontend	Streamlit
Machine Learning	Scikit-learn (Logistic Regression)
Visualization	Matplotlib
Data Handling	Pandas, NumPy

Requirements ->
Dependencies listed in requirements.txt:

streamlit
pandas
numpy
scikit-learn
matplotlib
💡 Optional Enhancements
Add top-lead filtering (Lead Score > threshold)

Display summary stats (avg, min, max score)

Customize theme, background, or logo

Add model comparison (e.g., RandomForest, XGBoost)

## 🧑‍💻 Author: ->
Rupesh Bhardwaj
🎓 B.Tech in Computer Science (AI & ML Specialization)
📍 Passionate about real-world ML solutions

## 📜 License: ->
This project is released under the MIT License.
