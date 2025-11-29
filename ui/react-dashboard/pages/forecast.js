import Link from "next/link";
import MetricCard from "@/components/MetricCard";
import SurgeChart from "@/components/SurgeChart";
import { usePrediction } from "@/context/PredictionContext";

export default function ForecastPage() {
  const { prediction } = usePrediction();

  if (!prediction) {
    return (
      <div className="card">
        <p>No prediction data yet.</p>
        <Link href="/" className="link-button">
          Generate Prediction
        </Link>
      </div>
    );
  }

  const pollution = prediction.pollution.pollution_impact;
  const festival = prediction.festival.festival_impact;
  const disease = prediction.disease.disease_impact;

  return (
    <div className="grid">
      <div className="metrics-grid">
        <MetricCard
          title="Pollution Severity"
          value={`${Math.round(pollution.severity_score * 100)}%`}
          description={`Risk: ${pollution.risk_level}`}
        />
        <MetricCard
          title="Festival Impact"
          value={`${Math.round(festival.severity_score * 100)}%`}
          description={festival.festival_name || "No major festival"}
        />
        <MetricCard
          title="Disease Severity"
          value={`${Math.round(disease.severity_score * 100)}%`}
          description={`Season: ${disease.season}`}
        />
        <MetricCard
          title="Overall Risk"
          value={prediction.prediction.risk_level}
          description={`Confidence ${Math.round(prediction.prediction.confidence * 100)}%`}
        />
      </div>

      <SurgeChart loads={prediction.prediction.loads} />

      <section className="card">
        <h3>Expected Patient Mix</h3>
        <ul className="tag-list">
          {[
            ...(pollution.expected_patient_types || []),
            ...(festival.expected_patient_types || []),
            ...(disease.expected_patient_types || []),
          ].map((item, idx) => (
            <li key={`${item}-${idx}`}>{item}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}

