import React, { useEffect } from "react";
import "./Dashboard.css";

export default function Modal({ open, onClose, title, children }) {
  useEffect(() => {
    function onKey(e) {
      if (e.key === "Escape") onClose();
    }
    if (open) window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="ds-modal-overlay" onClick={onClose}>
      <div
        className="ds-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <div className="ds-modal-header">
          <h3>{title}</h3>
          <button className="ds-close" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>
        <div className="ds-modal-body">{children}</div>
      </div>
    </div>
  );
}
