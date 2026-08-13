# Smart Irrigation Advisory System 🌾💧

A professional, full-stack application that provides data-driven, crop-specific irrigation recommendations using real-time soil moisture and weather data. 

## Features
- **Smart Advisory Engine**: Rule-based recommendation engine powered by **Pandas** that calculates exact water requirements (in mm and Litres) tailored to the specific crop, growth stage, soil moisture, and weather forecast.
- **Analytics Dashboard**: Comprehensive visualization of water usage trends and recommendation adherence scores using both **Matplotlib** (server-side generation) and **Plotly** (interactive client-side visualization).
- **Full-Stack Architecture**: Built with a **React** (Vite) frontend and a **Python Flask** backend.
- **Dual Storage Modes**: 
  - *Production*: **Firebase Firestore** and **Firebase Authentication**.
  - *Local Demo*: Seamlessly falls back to an in-memory JSON Mock DB with seeded dummy data for immediate local testing without cloud credentials.

## Technology Stack (Hackathon Compliant)
1. **Flask (Python)**: High-performance backend API serving 20+ endpoints.
2. **Pandas**: Used heavily in the backend for advisory batch-evaluation, water usage aggregation, and adherence analytics.
3. **Matplotlib & Plotly**: Used for creating rich analytical charts both as Base64 images and interactive React components.
4. **Firebase**: Used for secure authentication and scalable NoSQL data storage.
5. **Vercel**: Configuration provided via `vercel.json` for seamless deployment.

## Running Locally

The application is configured as a single unified server. The Flask backend will automatically serve the built React frontend on port `5001`.

### 1. Setup Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Setup Frontend
```bash
cd frontend
npm install
npm run build
```

### 3. Run the Unified Server
```bash
cd backend
python app.py
```
Visit **http://localhost:5001** to see the application.

## Deployment to Vercel

The repository contains a `vercel.json` configuration file tailored to deploy the Python Flask backend and React frontend seamlessly.

1. Push this repository to GitHub.
2. Go to your **[Vercel Dashboard](https://vercel.com/)**.
3. Click **Add New... > Project**.
4. Import your GitHub repository (`Garadurgaprasad/Smart-Irrigation-Advisory-System`).
5. Ensure the framework preset is set to **Vite** (Vercel usually detects this automatically).
6. Click **Deploy**. Vercel will automatically build the React app and map your Flask API to serverless functions using `@vercel/python`!
