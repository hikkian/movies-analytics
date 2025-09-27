# 🎬 CineAnalytics

**Company Name:** CineAnalytics  
**Role:** Data Analyst  

## 📌 Project Overview
CineAnalytics is a fictional analytics company focused on exploring trends in the global movie industry.  
Our mission is to help studios, directors, and streaming services understand viewer preferences, rating patterns,  
and production trends through comprehensive SQL analytics and visualizations.

This project demonstrates a full data-analysis pipeline:
- Relational database design (PostgreSQL)
- Data import and cleaning
- SQL queries for insights
- Python integration for automated analysis

---

## 🗂️ Database Schema
Below is the core ER diagram:

![ER Diagram](images/er_diagram.png)

**Tables**
- **genres**: Stores all movie genres  
- **directors**: Contains information about movie directors  
- **movies**: Holds core movie details and links each movie to a genre and a director  
- **actors**: Lists all actors  
- **movie_actor**: Many-to-many link between movies and actors  
- **users**: Stores registered users who can rate movies  
- **ratings**: User ratings for movies

---

## 🚀 How to Run the Project

### 1️⃣ Requirements
- **Python 3.10+**
- **PostgreSQL 15+**
- `psycopg2`, `tabulate` (install with `pip install -r requirements.txt`)

### 2️⃣ Set up PostgreSQL
1. Create the database:
   ```bash
   createdb movies_db
