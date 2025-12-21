import React, { useState, useEffect } from "react";
import "./Dashboard.css";
import Modal from "./Modal";

const priorityRank = (p) => ({ High: 3, Medium: 2, Low: 1 }[p] || 0);

function SimpleBarChart({ items }) {
  if (!items || items.length === 0) return null;
  const max = Math.max(...items.map((i) => i.count));
  const width = 520;
  const barGap = 8;
  const barWidth = Math.max(
    40,
    Math.floor((width - (items.length - 1) * barGap) / items.length)
  );

  return (
    <svg
      width="100%"
      viewBox={`0 0 ${width} 160`}
      preserveAspectRatio="xMidYMid meet"
    >
      {items.map((it, idx) => {
        const h = Math.round((it.count / max) * 90);
        const x = idx * (barWidth + barGap);
        const y = 110 - h;
        return (
          <g key={it.disease} transform={`translate(${x},0)`}>
            <rect
              x={0}
              y={y}
              width={barWidth}
              height={h}
              rx={6}
              fill="#3b82f6"
              opacity={0.9}
            />
            <text
              x={barWidth / 2}
              y={130}
              textAnchor="middle"
              fontSize={12}
              fill="#111"
            >
              {it.disease}
            </text>
            <text
              x={barWidth / 2}
              y={y - 4}
              textAnchor="middle"
              fontSize={11}
              fill="#111"
            >
              {it.count}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

export default function Dashboard() {
  const [trends, setTrends] = useState([]);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(null);
  const [selectedDetails, setSelectedDetails] = useState(null);
  const [page, setPage] = useState(1);
  const per_page = 10;
  const [totalPages, setTotalPages] = useState(1);
  const [report, setReport] = useState(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const tRes = await fetch("/api/dashboard/trends");
        const tJson = await tRes.json();
        const pRes = await fetch(`/api/dashboard/patients?page=${page}&per_page=${per_page}`);
        const pJson = await pRes.json();
        if (!mounted) return;
        setTrends(tJson.trends || []);
        // sort patients High -> Low
        const sorted = (pJson.patients || [])
          .slice()
          .sort((a, b) => priorityRank(b.priority) - priorityRank(a.priority));
        setPatients(sorted);
        if (pJson.meta && pJson.meta.total_pages) setTotalPages(pJson.meta.total_pages);
      } catch (err) {
        if (!mounted) return;
        setError(err.message || String(err));
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, [page]);

  async function openPatient(p) {
    setSelected(p);
    setSelectedDetails(null);
    try {
      const res = await fetch(`/api/patients/${p.id}`);
      const json = await res.json();
      setSelectedDetails(json.patient);
    } catch (err) {
      setSelectedDetails({ error: err.message || String(err) });
    }
  }

  async function generateReport() {
    setReport(null);
    try {
      const res = await fetch(`/api/dashboard/report?page=${page}&per_page=${per_page}`);
      const json = await res.json();
      setReport(json.report || json.report_text || 'No report returned');
    } catch (err) {
      setReport('Error generating report: ' + (err.message || String(err)));
    }
  }

  return (
    <div className="ds-container">
      <h2>Healthcare Dashboard</h2>

      {loading && <div>Loading dashboard…</div>}
      {error && <div style={{ color: "crimson" }}>Error: {error}</div>}

      {!loading && !error && (
        <>
          <div style={{ marginBottom: 16 }}>
            <h4>Current seasonal disease distribution</h4>
            <div style={{ background: "#fff", padding: 12, borderRadius: 10 }}>
              <SimpleBarChart items={trends} />
            </div>
          </div>

          <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:12}}>
            <div />
            <div style={{display:'flex',gap:8}}>
              <button onClick={() => { if (page>1) setPage(p => p-1) }} disabled={page<=1}>Prev</button>
              <div style={{alignSelf:'center'}}>Page {page} / {totalPages}</div>
              <button onClick={() => { if (page<totalPages) setPage(p => p+1) }} disabled={page>=totalPages}>Next</button>
              <button onClick={generateReport}>Generate report</button>
            </div>
          </div>

          <div className="ds-card">
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <h3 style={{ margin: 0 }}>Current Patients</h3>
              <div className="ds-badge">{patients.length} patients</div>
            </div>

            <table className="ds-table" aria-label="Current patients">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Age</th>
                  <th>Priority</th>
                  <th>Province</th>
                </tr>
              </thead>
              <tbody>
                {patients.map((p) => (
                  <tr
                    key={p.id}
                    onClick={() => openPatient(p)}
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") openPatient(p);
                    }}
                  >
                    <td>{p.name}</td>
                    <td>{p.age}</td>
                    <td>{p.priority}</td>
                    <td>{p.province}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <Modal
            open={!!selected}
            onClose={() => {
              setSelected(null);
              setSelectedDetails(null);
            }}
            title={selected ? selected.name : ""}
          >
            {selectedDetails ? (
              selectedDetails.error ? (
                <div style={{ color: "crimson" }}>
                  Error loading details: {selectedDetails.error}
                </div>
              ) : (
                <div>
                  <p>
                    <strong>Age:</strong> {selectedDetails.age}
                  </p>
                  <p>
                    <strong>Province:</strong> {selectedDetails.province}
                  </p>
                  <p>
                    <strong>Priority:</strong> {selectedDetails.priority}
                  </p>
                  <p>
                    <strong>Notes:</strong> {selectedDetails.notes}
                  </p>
                  <hr />
                  <p>
                    <strong>DOB:</strong> {selectedDetails.details?.dob}
                  </p>
                  <p>
                    <strong>Postal:</strong> {selectedDetails.details?.postal}
                  </p>
                  <p>
                    <strong>Contact:</strong> {selectedDetails.details?.contact}
                  </p>
                  <p>
                    <strong>Medical history:</strong>{" "}
                    {selectedDetails.details?.medical_history}
                  </p>
                  <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
                    <button
                      onClick={() => {
                        alert("Assigned");
                        setSelected(null);
                        setSelectedDetails(null);
                      }}
                    >
                      Assign
                    </button>
                    <button
                      onClick={() => {
                        alert("Message sent");
                        setSelected(null);
                        setSelectedDetails(null);
                      }}
                    >
                      Message
                    </button>
                  </div>
                </div>
              )
            ) : (
              <div>Loading patient details…</div>
            )}
          </Modal>
          {report && (
            <div style={{marginTop:12,background:'#fff',padding:12,borderRadius:8}}>
              <h4>Generated report (page {page})</h4>
              <pre style={{whiteSpace:'pre-wrap'}}>{report}</pre>
            </div>
          )}
        </>
      )}
    </div>
  );
}
