import React, { useState, useEffect } from "react";
import "./ResponsiveCard.css";
import { processReferral } from "../api/referralApi";

/**
 * ResponsiveCard
 * - Click (or press Enter) the card to flip and reveal details.
 * - Click the heart to toggle "like" without flipping.
 * Props: `title`, `summary`, `tags` (array)
 * This component is standalone and easy to reuse.
 */
export default function ResponsiveCard({
  title = "Patient Referral",
  summary = "Short referral summary goes here.",
  tags = ["Urgent", "Cardiology"],
  fetchOnMount = true,
  referralText = "Patient reports chest pain and dizziness, ongoing 3 days.",
  province = "ontario",
}) {
  const [flipped, setFlipped] = useState(false);
  const [liked, setLiked] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiData, setApiData] = useState(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      if (!fetchOnMount) return;
      setLoading(true);
      setError(null);
      try {
        const res = await processReferral({
          referral_text: referralText,
          province,
        });
        if (!mounted) return;
        setApiData(res);
      } catch (err) {
        if (!mounted) return;
        setError(err?.message || String(err));
      } finally {
        if (!mounted) return;
        setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, [fetchOnMount, referralText, province]);

  return (
    <div className={`rc-card ${flipped ? "flipped" : ""}`}>
      <div
        className="rc-inner"
        role="button"
        tabIndex={0}
        onClick={() => setFlipped((s) => !s)}
        onKeyDown={(e) => {
          if (e.key === "Enter") setFlipped((s) => !s);
        }}
        aria-pressed={flipped}
      >
        <div className="rc-front">
          <div className="rc-header">
            <h2 className="rc-title">{title}</h2>
            <button
              className={`rc-like ${liked ? "active" : ""}`}
              onClick={(e) => {
                e.stopPropagation();
                setLiked((s) => !s);
              }}
              aria-pressed={liked}
              title={liked ? "Unlike" : "Like"}
            >
              {liked ? "♥" : "♡"}
            </button>
          </div>

          <p className="rc-summary">{summary}</p>

          <div className="rc-tags">
            {tags.map((t) => (
              <span key={t} className="rc-tag">
                {t}
              </span>
            ))}
          </div>

          <div className="rc-footer">
            {loading && <span>Loading data…</span>}
            {error && <span style={{ color: "crimson" }}>Error: {error}</span>}
            {!loading && apiData && (
              <div style={{ marginTop: 8 }}>
                <strong>Score:</strong> {apiData.priority_score ?? "—"}
              </div>
            )}
            {!loading && !apiData && !error && (
              <span>Tap card to flip for more details</span>
            )}
          </div>
        </div>

        <div className="rc-back">
          <h3>Referral Details</h3>
          <dl>
            <dt>Age</dt>
            <dd>{apiData?.parsed?.patient_age ?? 65}</dd>
            <dt>Priority</dt>
            <dd>
              {apiData?.urgency?.urgency_label ?? apiData?.priority_score
                ? "See score"
                : "—"}
            </dd>
            <dt>Notes</dt>
            <dd>
              {apiData?.explanation?.summary ??
                apiData?.parsed?.notes ??
                "No notes available."}
            </dd>
          </dl>

          <div className="rc-actions">
            <button
              onClick={(e) => {
                e.stopPropagation();
                alert("Assigned");
              }}
            >
              Assign
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                alert("Message sent");
              }}
            >
              Message
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
