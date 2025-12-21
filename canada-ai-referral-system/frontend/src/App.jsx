import React from "react";
import ReferralList from "./components/ReferralList";
import Dashboard from "./components/Dashboard";

export default function App() {
  return (
    <div style={{ padding: 20, maxWidth: 980, margin: "0 auto" }}>
      <h1>Canada AI Referral System (Frontend)</h1>
      <p>Prototype UI. Example responsive component below.</p>

      <Dashboard />
    </div>
  );
}
