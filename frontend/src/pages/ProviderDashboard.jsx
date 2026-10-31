import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
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

export default function ProviderDashboard() {
  const { user } = useAuth();
  const location = useLocation();
  const stats = useFetch(() => api.providerStats(), []);
  const meals = useFetch(() => api.getMeals({ provider_id: user.id, limit: 20 }), [user.id]);
  const [target, setTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [notice, setNotice] = useState(location.state?.notice || "");
  const [actionError, setActionError] = useState("");

  async function confirmDelete() {
    setDeleting(true);
    setActionError("");
    try {
      await api.deleteMeal(target.id);
      setNotice(`"${target.name}" was deleted.`);
    } catch (err) {
      setActionError(err.message);
    } finally {
      setDeleting(false);
      setTarget(null);
      meals.reload();
      stats.reload();
    }
  }

  const s = stats.data;
  return (
    <div className="container section">
      <div className="section-head">
        <h1>Provider dashboard</h1>
        <div className="row-actions">
          <Link to="/provider/reservations" className="btn btn-outline btn-md">View reservations</Link>
          <Link to="/provider/meals/new" className="btn btn-primary btn-md">+ Add meal</Link>
        </div>
      </div>
      <p className="muted">Welcome, {user.name}.</p>

      {notice && <div className="alert alert-success" role="status">{notice}</div>}
      {actionError && <div className="alert alert-error" role="alert">{actionError}</div>}

      {stats.loading && <LoadingSpinner label="Loading statistics..." />}
      {stats.error && <ErrorMessage message={stats.error} onRetry={stats.reload} />}
      {s && (
        <div className="stat-grid">
          <div className="stat"><strong>{s.active_listings}</strong>Active listings</div>
          <div className="stat"><strong>{s.expired_listings}</strong>Expired listings</div>
          <div className="stat"><strong>{s.total_reservations}</strong>Total reservations</div>
          <div className="stat"><strong>{s.collected_reservations}</strong>Collected</div>
        </div>
      )}

      <h2>Your listings</h2>
      {meals.loading && <LoadingSpinner label="Loading your listings..." />}
      {meals.error && <ErrorMessage message={meals.error} onRetry={meals.reload} />}
      {meals.data && meals.data.items.length === 0 && (
        <EmptyState title="You have no listings yet" text="Share some food with your community."
          action={<Link to="/provider/meals/new" className="btn btn-primary btn-md">Add your first meal</Link>} />
      )}
      {meals.data && meals.data.items.length > 0 && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Meal</th><th>Category</th><th>Portions</th><th>Pick up before</th><th>Status</th><th></th></tr>
            </thead>
            <tbody>
              {meals.data.items.map((m) => (
                <tr key={m.id}>
                  <td><Link to={`/meals/${m.id}`}>{m.name}</Link><div className="muted small">{m.location.name}, {m.location.city}</div></td>
                  <td>{m.category.name}</td>
                  <td>{m.quantity}</td>
                  <td>{formatDateTime(m.available_until)}</td>
                  <td><StatusBadge status={m.display_status} expiringSoon={m.expiring_soon} /></td>
                  <td>
                    <div className="row-actions">
                      <Link to={`/provider/meals/${m.id}/edit`} className="btn btn-outline btn-sm">Edit</Link>
                      <Button variant="outline" size="sm" onClick={() => setTarget(m)}>Delete</Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={Boolean(target)} title="Delete this meal?" onClose={() => setTarget(null)}
        footer={<><Button variant="outline" onClick={() => setTarget(null)}>Keep it</Button><Button variant="danger" loading={deleting} onClick={confirmDelete}>Yes, delete</Button></>}>
        {target && <p>"{target.name}" will be removed for everyone. This cannot be undone.</p>}
      </Modal>
    </div>
  );
}