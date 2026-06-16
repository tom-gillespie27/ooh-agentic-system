import { MapPin } from "lucide-react";

export default function BillboardList({ billboards, selectedId, onSelect, loading }) {
  if (loading) {
    return <div className="skeleton-list" aria-label="Loading billboards" />;
  }

  return (
    <nav className="billboard-list" aria-label="Billboards">
      {billboards.map((billboard) => (
        <button
          className={`billboard-button ${billboard.id === selectedId ? "active" : ""}`}
          type="button"
          key={billboard.id}
          onClick={() => onSelect(billboard.id)}
        >
          <MapPin size={18} aria-hidden="true" />
          <span>
            <strong>{billboard.location}</strong>
            <small>{billboard.name}</small>
          </span>
        </button>
      ))}
    </nav>
  );
}
