export function formatDateTime(iso) {
  return new Date(iso).toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function timeLeft(iso) {
  const minutes = Math.floor((new Date(iso) - Date.now()) / 60000);
  if (minutes <= 0) return "Ended";
  if (minutes < 60) return `${minutes} min left`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ${minutes % 60}m left`;
  return `${Math.floor(hours / 24)} days left`;
}

// Turns an ISO time into the "2026-10-30T14:30" text a datetime-local field needs.
export function toLocalInput(iso) {
  const d = new Date(iso);
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}