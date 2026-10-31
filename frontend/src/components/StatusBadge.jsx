const LABELS = {
  AVAILABLE: ["Available", "green"],
  EXPIRING: ["Expiring soon", "amber"],
  FULLY_RESERVED: ["Fully reserved", "gray"],
  EXPIRED: ["Expired", "red"],
  UNAVAILABLE: ["Unavailable", "gray"],
  RESERVED: ["Reserved", "blue"],
  COLLECTED: ["Collected", "green"],
  CANCELLED: ["Cancelled", "gray"],
};

export default function StatusBadge({ status, expiringSoon = false }) {
  const key = status === "AVAILABLE" && expiringSoon ? "EXPIRING" : status;
  const [label, tone] = LABELS[key] || [status, "gray"];
  return <span className={`badge badge-${tone}`}>{label}</span>;
}