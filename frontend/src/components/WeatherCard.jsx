import { CloudSun } from "lucide-react";

export default function WeatherCard({ weather, summary }) {
  const temp = typeof weather?.temp === "number" ? Math.round(weather.temp) : null;

  return (
    <section className="panel metric-panel">
      <div className="section-heading">
        <CloudSun size={18} aria-hidden="true" />
        <h3>Current Weather</h3>
      </div>
      <div className="metric-row">
        <span className="metric-value">{temp === null ? "--" : `${temp}°F`}</span>
        <span className="metric-label">{weather?.condition ?? "Unknown"}</span>
      </div>
      <p>{summary ?? weather?.description ?? "Weather context unavailable."}</p>
    </section>
  );
}
