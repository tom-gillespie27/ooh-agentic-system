import { useEffect, useMemo, useState } from "react";
import {
  AlertCircle,
  BarChart3,
  CheckCircle2,
  Loader2,
  RefreshCw,
} from "lucide-react";
import AgentTrace from "./components/AgentTrace.jsx";
import BillboardList from "./components/BillboardList.jsx";
import CreativeCard from "./components/CreativeCard.jsx";
import EventCard from "./components/EventCard.jsx";
import WeatherCard from "./components/WeatherCard.jsx";

const API_BASE = "/api";

function normalizeDecision(payload) {
  const trace = payload?.decision?.trace ?? [];
  const weatherTrace = trace.find((item) => item.tool === "get_weather");
  const eventTrace = trace.find((item) => item.tool === "get_local_events");

  return {
    billboard: payload?.billboard,
    creative: payload?.creative,
    decision: payload?.decision,
    weather: weatherTrace?.output,
    events: eventTrace?.output?.events ?? [],
    trace,
  };
}

export default function App() {
  const [billboards, setBillboards] = useState([]);
  const [creatives, setCreatives] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [decisionState, setDecisionState] = useState({
    data: null,
    loading: false,
    error: "",
  });
  const [bootState, setBootState] = useState({
    loading: true,
    error: "",
  });

  useEffect(() => {
    let ignore = false;

    async function loadInitialData() {
      try {
        const [billboardRes, creativeRes] = await Promise.all([
          fetch(`${API_BASE}/billboards`),
          fetch(`${API_BASE}/creatives`),
        ]);

        if (!billboardRes.ok || !creativeRes.ok) {
          throw new Error("Backend returned an error while loading inventory.");
        }

        const [billboardData, creativeData] = await Promise.all([
          billboardRes.json(),
          creativeRes.json(),
        ]);

        if (!ignore) {
          setBillboards(billboardData);
          setCreatives(creativeData);
          setSelectedId(billboardData[0]?.id ?? "");
          setBootState({ loading: false, error: "" });
        }
      } catch (error) {
        if (!ignore) {
          setBootState({
            loading: false,
            error: error.message || "Unable to reach the backend.",
          });
        }
      }
    }

    loadInitialData();

    return () => {
      ignore = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedId) return;

    let ignore = false;

    async function loadDecision() {
      setDecisionState((current) => ({
        ...current,
        loading: true,
        error: "",
      }));

      try {
        const response = await fetch(`${API_BASE}/decision/${selectedId}`);
        if (!response.ok) {
          throw new Error("Decision request failed.");
        }

        const payload = await response.json();
        if (payload.error) {
          throw new Error(payload.error);
        }

        if (!ignore) {
          setDecisionState({
            data: normalizeDecision(payload),
            loading: false,
            error: "",
          });
        }
      } catch (error) {
        if (!ignore) {
          setDecisionState({
            data: null,
            loading: false,
            error: error.message || "Unable to generate a decision.",
          });
        }
      }
    }

    loadDecision();

    return () => {
      ignore = true;
    };
  }, [selectedId]);

  const selectedBillboard = useMemo(
    () => billboards.find((billboard) => billboard.id === selectedId),
    [billboards, selectedId]
  );

  const decisionData = decisionState.data;
  const decision = decisionData?.decision;

  function refreshDecision() {
    if (!selectedId) return;
    setSelectedId("");
    requestAnimationFrame(() => setSelectedId(selectedId));
  }

  return (
    <main className="app-shell">
      <aside className="sidebar" aria-label="Billboard inventory">
        <div className="brand-block">
          <div>
            <p className="eyebrow">OOH Agent</p>
            <h1>Decision Engine</h1>
          </div>
          <BarChart3 size={24} aria-hidden="true" />
        </div>

        {bootState.error ? (
          <div className="status-message error">
            <AlertCircle size={18} />
            <span>{bootState.error}</span>
          </div>
        ) : (
          <BillboardList
            billboards={billboards}
            selectedId={selectedId}
            onSelect={setSelectedId}
            loading={bootState.loading}
          />
        )}
      </aside>

      <section className="workspace" aria-live="polite">
        <header className="workspace-header">
          <div>
            <p className="eyebrow">Live contextual decision</p>
            <h2>{selectedBillboard?.name ?? "Select a billboard"}</h2>
            {selectedBillboard ? (
              <p className="location-line">{selectedBillboard.location}</p>
            ) : null}
          </div>

          <button
            className="icon-button"
            type="button"
            onClick={refreshDecision}
            disabled={!selectedId || decisionState.loading}
            title="Refresh decision"
            aria-label="Refresh decision"
          >
            {decisionState.loading ? (
              <Loader2 className="spin" size={18} />
            ) : (
              <RefreshCw size={18} />
            )}
          </button>
        </header>

        {decisionState.loading ? (
          <div className="decision-loading">
            <Loader2 className="spin" size={22} />
            <span>Evaluating weather, events, and creative fit...</span>
          </div>
        ) : null}

        {decisionState.error ? (
          <div className="status-message error wide">
            <AlertCircle size={18} />
            <span>{decisionState.error}</span>
          </div>
        ) : null}

        {decisionData && !decisionState.loading ? (
          <div className="decision-grid">
            <WeatherCard weather={decisionData.weather} summary={decision?.weather_summary} />
            <EventCard events={decisionData.events} summary={decision?.event_summary} />
            <CreativeCard
              creative={decisionData.creative}
              decision={decision}
              creatives={creatives}
            />

            <section className="panel reasoning-panel">
              <div className="section-heading">
                <CheckCircle2 size={18} aria-hidden="true" />
                <h3>Reasoning</h3>
              </div>
              <p>{decision?.reasoning ?? "No reasoning returned."}</p>
            </section>

            <AgentTrace trace={decisionData.trace} hasDecision={Boolean(decision)} />
          </div>
        ) : null}
      </section>
    </main>
  );
}
