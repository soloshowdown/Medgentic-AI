import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";

export default function SurgeChart({ loads }) {
  if (!loads) return null;

  const chartData = [
    { name: "OPD", value: loads.opd || 0 },
    { name: "Emergency", value: loads.emergency || 0 },
    { name: "ICU", value: loads.icu || 0 },
  ];

  return (
    <div className="card">
      <h3>Surge Projection</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={3} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

