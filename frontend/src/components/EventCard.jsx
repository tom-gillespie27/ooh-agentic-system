import { CalendarDays } from "lucide-react";

export default function EventCard({ events, summary }) {
  return (
    <section className="panel events-panel">
      <div className="section-heading">
        <CalendarDays size={18} aria-hidden="true" />
        <h3>Local Events</h3>
      </div>
      {events.length ? (
        <ul className="event-list">
          {events.slice(0, 4).map((event, index) => (
            <li key={`${event.name}-${event.date}-${index}`}>
              <strong>{event.name}</strong>
              <span>{[event.date, event.category].filter(Boolean).join(" · ")}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p>No nearby events returned.</p>
      )}
      {summary ? <p className="subtle-copy">{summary}</p> : null}
    </section>
  );
}
