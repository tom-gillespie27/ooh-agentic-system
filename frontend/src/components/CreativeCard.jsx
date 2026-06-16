import { BadgeCheck, Trophy } from "lucide-react";

function creativeName(creatives, id) {
  return creatives.find((creative) => creative.id === id)?.name ?? id;
}

export default function CreativeCard({ creative, decision, creatives }) {
  const confidence = Math.max(0, Math.min(100, Number(decision?.confidence ?? 0)));
  const rankings = decision?.rankings ?? [];

  return (
    <section className="panel creative-panel">
      <div className="section-heading">
        <Trophy size={18} aria-hidden="true" />
        <h3>Selected Creative</h3>
      </div>

      <div className="selected-creative">
        <div>
          <strong>{creative?.name ?? decision?.selected_creative_id ?? "Pending"}</strong>
          <span>{creative?.description ?? "Creative metadata unavailable."}</span>
        </div>
        <BadgeCheck size={26} aria-hidden="true" />
      </div>

      <div className="confidence-block">
        <div className="confidence-topline">
          <span>Confidence</span>
          <strong>{confidence}%</strong>
        </div>
        <div className="bar-track" aria-hidden="true">
          <span className="bar-fill confidence-fill" style={{ width: `${confidence}%` }} />
        </div>
      </div>

      <div className="ranking-block">
        <h4>Creative Scoring</h4>
        {rankings.length ? (
          <ul className="ranking-list">
            {rankings.map((ranking) => {
              const score = Math.max(0, Math.min(100, Number(ranking.score ?? 0)));
              const name = creativeName(creatives, ranking.creative);

              return (
                <li key={ranking.creative}>
                  <span className="ranking-name">{name}</span>
                  <span className="ranking-bar" aria-hidden="true">
                    <span style={{ width: `${score}%` }} />
                  </span>
                  <strong>{score}</strong>
                </li>
              );
            })}
          </ul>
        ) : (
          <p>No creative rankings returned.</p>
        )}
      </div>
    </section>
  );
}
