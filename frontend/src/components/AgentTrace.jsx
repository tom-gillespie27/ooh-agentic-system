import { CheckCircle2, Route } from "lucide-react";

const toolLabels = {
  get_weather: "Weather API",
  get_local_events: "Ticketmaster API",
};

export default function AgentTrace({ trace, hasDecision }) {
  const steps = [
    ...trace.map((item) => toolLabels[item.tool] ?? item.tool),
    "Creative Evaluation",
    ...(hasDecision ? ["Final Decision"] : []),
  ];

  return (
    <section className="panel trace-panel">
      <div className="section-heading">
        <Route size={18} aria-hidden="true" />
        <h3>Agent Trace</h3>
      </div>
      <ol className="trace-list">
        {steps.map((step, index) => (
          <li key={`${step}-${index}`}>
            <CheckCircle2 size={17} aria-hidden="true" />
            <span>{step}</span>
          </li>
        ))}
      </ol>
    </section>
  );
}
