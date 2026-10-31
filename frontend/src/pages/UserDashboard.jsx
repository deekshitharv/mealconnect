import { useState } from "react";
import { Link } from "react-router-dom";
import Button from "../components/Button";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import LoadingSpinner from "../components/LoadingSpinner";
import Modal from "../components/Modal";
import StatusBadge from "../components/StatusBadge";
import { useAuth } from "../hooks/useAuth";
import useFetch from "../hooks/useFetch";
import { api } from "../services/api";
import { formatDateTime } from "../utils/format";

function ReservationTable({ rows, onCancel }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Meal</th><th>Location</th><th>Qty</th><th>Reserved</th><th>Pick up before</th><th>Status</th><th></th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>
                <Link to={`/meals/${r.meal.id}`}>{r.meal.name}</Link>
                <div className="muted small">by {r.meal.provider.name}</div>
              </td>
              <td>{r.meal.location.name}, {r.meal.location.city}</td>
              <td>{r.quantity}</td>
              <td>{formatDateTime(r.reserved_at)}</td>
              <td>{formatDateTime(r.meal.available_until)}</td>
              <td><StatusBadge status={r.display_status} /></td>
              <td>
                {onCancel && r.is_active && (
                  <Button variant="outline" size="sm" onClick={() => onCancel(r)}>Cancel</Button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function UserDashboard() {
  const { user } = useAuth();
  const { data, loading, error, reload } = useFetch(() => api.myReservations({ limit: 50 }), []);
  const [cancelTarget, setCancelTarget] = useState(null);
  const [cancelling, setCancelling] = useState(false);
  const [notice, setNotice] = useState("");
  const [actionError, setActionError] = useState("");

  async function confirmCancel() {
    setCancelling(true);
    setActionError("");
    try {
      await api.cancelReservation(cancelTarget.id);
      setNotice(`Reservation for ${cancelTarget.meal.name} was cancelled.`);
      setCancelTarget(null);
      reload();
    } catch (err) {
      setActionError(err.message);
      setCancelTarget(null);
      reload();
    } finally {
      setCancelling(false);
    }
  }

  const items = data?.items || [];
  const active = items.filter((r) => r.is_active);
  const history = items.filter((r) => !r.is_active);

  return (
    <div className="container section">
      <h1>My dashboard</h1>

      <div className="card profile">
        <div className="avatar">{user.name.charAt(0).toUpperCase()}</div>
        <div>
          <h3>{user.name}</h3>
          <p className="muted small">{user.email} · {user.role}</p>
        </div>
      </div>

      {notice && <div className="alert alert-success" role="status">{notice}</div>}
      {actionError && <div className="alert alert-error" role="alert">{actionError}</div>}
      {loading && <LoadingSpinner label="Loading your reservations..." />}
      {error && <ErrorMessage message={error} onRetry={reload} />}

      {data && (
        <>
          <h2>Active reservations</h2>
          {active.length === 0 ? (
            <EmptyState title="No active reservations" text="Find a meal and reserve a portion."
              action={<Link to="/meals" className="btn btn-primary btn-md">Browse meals</Link>} />
          ) : (
            <ReservationTable rows={active} onCancel={setCancelTarget} />
          )}

          <h2 className="gap-top">Reservation history</h2>
          {history.length === 0 ? <p className="muted">Collected, cancelled and expired reservations show up here.</p> : <ReservationTable rows={history} />}
        </>
      )}

      <Modal
        open={Boolean(cancelTarget)}
        title="Cancel this reservation?"
        onClose={() => setCancelTarget(null)}
        footer={
          <>
            <Button variant="outline" onClick={() => setCancelTarget(null)}>Keep it</Button>
            <Button variant="danger" loading={cancelling} onClick={confirmCancel}>Yes, cancel</Button>
          </>
        }
      >
        {cancelTarget && <p>{cancelTarget.quantity} × {cancelTarget.meal.name} will go back to other people.</p>}
      </Modal>
    </div>
  );
}