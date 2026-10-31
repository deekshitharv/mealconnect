import { useState } from "react";
import { Link } from "react-router-dom";
import Button from "../components/Button";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import LoadingSpinner from "../components/LoadingSpinner";
import Pagination from "../components/Pagination";
import StatusBadge from "../components/StatusBadge";
import useFetch from "../hooks/useFetch";
import { api } from "../services/api";
import { formatDateTime } from "../utils/format";

export default function ProviderReservations() {
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);
  const { data, loading, error, reload } = useFetch(
    () => api.providerReservations({ status, page, limit: 10 }),
    [status, page],
  );
  const [busyId, setBusyId] = useState(null);
  const [notice, setNotice] = useState("");
  const [actionError, setActionError] = useState("");

  async function collect(r) {
    setBusyId(r.id);
    setNotice("");
    setActionError("");
    try {
      await api.collectReservation(r.id);
      setNotice(`${r.user.name}'s reservation was marked as collected.`);
    } catch (err) {
      setActionError(err.message);
    } finally {
      setBusyId(null);
      reload();
    }
  }

  return (
    <div className="container section">
      <Link to="/provider/dashboard">← Back to dashboard</Link>
      <h1>Reservations on your meals</h1>

      <div className="filters">
        <div className="field">
          <label htmlFor="status">Status</label>
          <select id="status" className="input" value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }}>
            <option value="">All</option>
            <option value="RESERVED">Reserved</option>
            <option value="COLLECTED">Collected</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>
      </div>

      {notice && <div className="alert alert-success" role="status">{notice}</div>}
      {actionError && <div className="alert alert-error" role="alert">{actionError}</div>}
      {loading && <LoadingSpinner label="Loading reservations..." />}
      {error && <ErrorMessage message={error} onRetry={reload} />}

      {data && data.items.length === 0 && <EmptyState title="No reservations yet" text="They will show up here when someone reserves your food." />}
      {data && data.items.length > 0 && (
        <>
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Customer</th><th>Meal</th><th>Qty</th><th>Reserved</th><th>Pick up before</th><th>Status</th><th></th></tr>
              </thead>
              <tbody>
                {data.items.map((r) => (
                  <tr key={r.id}>
                    <td>{r.user.name}<div className="muted small">{r.user.email}</div></td>
                    <td>{r.meal.name}</td>
                    <td>{r.quantity}</td>
                    <td>{formatDateTime(r.reserved_at)}</td>
                    <td>{formatDateTime(r.meal.available_until)}</td>
                    <td><StatusBadge status={r.display_status} /></td>
                    <td>
                      {r.is_active && (
                        <Button size="sm" variant="green" loading={busyId === r.id} onClick={() => collect(r)}>Mark as collected</Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination page={data.page} totalPages={data.total_pages} onChange={setPage} />
        </>
      )}
    </div>
  );
}