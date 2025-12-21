import React from "react";
import ResponsiveCard from "./ResponsiveCard";

const sampleReferrals = [
  {
    id: "r1",
    title: "John Doe — Cardiology",
    referralText:
      "65-year-old male with intermittent chest pain for 3 days, shortness of breath on exertion.",
    province: "ontario",
    tags: ["Cardiology", "High Priority"],
  },
  {
    id: "r2",
    title: "Jane Smith — Orthopedics",
    referralText:
      "45-year-old female with progressive knee pain and reduced mobility after fall.",
    province: "bc",
    tags: ["Orthopedics", "Elective"],
  },
  {
    id: "r3",
    title: "Carlos M — Neurology",
    referralText:
      "58-year-old with new onset headaches and intermittent visual changes.",
    province: "alberta",
    tags: ["Neurology", "Investigate"],
  },
];

export default function ReferralList() {
  return (
    <section
      style={{
        display: "grid",
        gap: 18,
        gridTemplateColumns: "repeat(auto-fit,minmax(280px,1fr))",
        alignItems: "start",
        marginTop: 18,
      }}
    >
      {sampleReferrals.map((r) => (
        <ResponsiveCard
          key={r.id}
          title={r.title}
          summary={r.referralText}
          tags={r.tags}
          fetchOnMount={true}
          referralText={r.referralText}
          province={r.province}
        />
      ))}
    </section>
  );
}
