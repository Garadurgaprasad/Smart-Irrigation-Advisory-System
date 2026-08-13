// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCM1HaSLRXiwL5oi7tQzwWJ2onhEgsWuIc",
  authDomain: "agrisense-1d0b3.firebaseapp.com",
  projectId: "agrisense-1d0b3",
  storageBucket: "agrisense-1d0b3.firebasestorage.app",
  messagingSenderId: "503163669221",
  appId: "1:503163669221:web:d1e880cf00001c1c5ea20c",
  measurementId: "G-QK68YCCBY1"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

export { app, analytics };
