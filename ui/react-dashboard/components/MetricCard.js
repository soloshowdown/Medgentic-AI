export default function MetricCard({ title, value, description }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <p className="metric">{value}</p>
      {description && <p className="description">{description}</p>}
    </div>
  );
}

