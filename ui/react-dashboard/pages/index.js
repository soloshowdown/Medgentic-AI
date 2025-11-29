import { useState } from "react";
import axios from "axios";
import Link from "next/link";
import { usePrediction } from "@/context/PredictionContext";
import MetricCard from "@/components/MetricCard";

const cities = ["Mumbai", "Delhi", "Bangalore", "Kolkata", "Chennai", "Hyderabad", "Pune"];
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function Home() {
  const today = new Date().toISOString().slice(0, 10);
  const [city, setCity] = useState("Mumbai");
  const [date, setDate] = useState(today);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { prediction, setPrediction } = usePrediction();

  const handleSubmit = async (evt) => {
    evt.preventDefault();
    setError("");
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/predict`, { city, date });
      setPrediction(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to fetch prediction");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid">
      <section className="card">
        <h2>Predict Hospital Load</h2>
        <p>Provide city and date to generate an AI-assisted surge plan.</p>
        <form className="form" onSubmit={handleSubmit}>
          <label>
            City
            <select value={city} onChange={(e) => setCity(e.target.value)}>
              {cities.map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </label>
          <label>
            Date
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? "Predicting..." : "Predict Hospital Load"}
          </button>
          {error && <p className="error">{error}</p>}
        </form>
      </section>

      {prediction && (
        <section className="card">
          <h2>Latest Prediction</h2>
          <p>{prediction.summary}</p>
          <div className="metrics-grid">
            <MetricCard title="OPD" value={`${prediction.prediction.loads.opd} pts`} />
            <MetricCard title="Emergency" value={`${prediction.prediction.loads.emergency} pts`} />
            <MetricCard title="ICU" value={`${prediction.prediction.loads.icu} beds`} />
            <MetricCard title="Risk Level" value={prediction.prediction.risk_level} />
          </div>
          <div className="actions">
            <Link href="/forecast" className="link-button">
              View Forecast
            </Link>
            <Link href="/resources" className="link-button secondary">
              Resource Plan
            </Link>
          </div>
        </section>
      )}
    </div>
  );
}

