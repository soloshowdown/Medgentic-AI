import Link from "next/link";
import { usePrediction } from "@/context/PredictionContext";

export default function ResourcesPage() {
  const { prediction } = usePrediction();

  if (!prediction) {
    return (
      <div className="card">
        <p>No resource plan yet.</p>
        <Link href="/" className="link-button">
          Generate Prediction
        </Link>
      </div>
    );
  }

  const plan = prediction.operations.resource_plan;

  const downloadPdf = () => {
    window.print();
  };

  return (
    <div className="grid">
      <section className="card">
        <div className="section-header">
          <h3>Staff Requirements</h3>
          <button onClick={downloadPdf} className="link-button secondary">
            Download as PDF
          </button>
        </div>
        <div className="metrics-grid">
          {Object.entries(plan.requirements.staff).map(([role, count]) => (
            <div key={role} className="card inset">
              <h4>{role}</h4>
              <p className="metric">{count}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <h3>Bed & ICU Allocation</h3>
        <div className="metrics-grid">
          {Object.entries(plan.requirements.beds).map(([type, count]) => (
            <div key={type} className="card inset">
              <h4>{type}</h4>
              <p className="metric">{count}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <h3>Supplies Checklist</h3>
        <ul className="checklist">
          {plan.checklist.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="card">
        <h3>Shift Recommendations</h3>
        <ul className="checklist">
          {plan.shift_plan.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
        <h4>Notes</h4>
        <ul className="checklist">
          {plan.notes.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}

