import { Link, useParams } from "react-router-dom";
import ErrorMessage from "../components/ErrorMessage";
import LoadingSpinner from "../components/LoadingSpinner";
import useFetch from "../hooks/useFetch";
import { api } from "../services/api";
import { formatDateTime } from "../utils/format";

export default function ReservationSuccess() {
  const { id } = useParams();
  const { data: r, loading, error, reload } = useFetch(() => api.getReservation(id), [id]);

  if (loading) return <LoadingSpinner label="Loading your reservation..." />;
  if (error) {
    return (
      <div className="container section">
        <ErrorMessage message={error} onRetry={reload} />
      </div>
    );
  }

  return (
    <div className="container section">
      <div className="card auth-card center">
        <div className="success-icon">✓</div>
        <h1>Reservation confirmed</h1>
        <p className="muted">Show this to the provider when you collect your food.</p>
        <ul className="meta left">
          <li>Reservation #{r.id}</li>
          <li>🍱 {r.quantity} × {r.meal.name}</li>
          <li>🏪 {r.meal.provider.name}</li>
          <li>📍 {r.meal.location.name}, {r.meal.location.address}, {r.meal.location.city}</li>
          <li>⏰ Collect before {formatDateTime(r.meal.available_until)}</li>
        </ul>
        <div className="stack">
          <Link to="/dashboard" className="btn btn-primary btn-md block">View my reservations</Link>
          <Link to="/meals" className="btn btn-outline btn-md block">Browse more meals</Link>
        </div>
      </div>
    </div>
  );
}