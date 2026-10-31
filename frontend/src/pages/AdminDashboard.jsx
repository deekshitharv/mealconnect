import { useState } from "react";
import { Link } from "react-router-dom";
import Button from "../components/Button";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import LoadingSpinner from "../components/LoadingSpinner";
import Modal from "../components/Modal";
import Pagination from "../components/Pagination";
import StatusBadge from "../components/StatusBadge";
import useFetch from "../hooks/useFetch";
import { api } from "../services/api";
import { formatDateTime } from "../utils/format";

// Shared loading / error / empty handling for each table.
function Section({ state, children }) {
  if (state.loading) return <LoadingSpinner label="Loading..." />;
  if (state.error) return <ErrorMessage message={state.error} onRetry={state.reload} />;
  if (!state.data || state.data.items.length === 0) return <EmptyState title="Nothing here yet" />;
  return children;
}

function UsersTab({ role }) {
  const [page, setPage] = useState(1);
  const state = useFetch(() => api.adminUsers({ role, page, limit: 10 }), [role, page]);
  const [target, setTarget] = useState(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });

  async function remove() {
    setBusy(true);
    try {
      await api.adminDeleteUser(target.id);
      setMessage({ type: "success", text: `${target.name} was deleted.` });
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    } finally {
      setBusy(false);
      setTarget(null);
      state.reload();
    }
  }

  return (
    <>
      {message.text && <div className={`alert alert-${message.type}`} role="status">{message.text}</div>}
      <Section state={state}>
        <div className="table-wrap">
          <table>
            <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Joined</th><th></th></tr></thead>
            <tbody>
              {state.data?.items.map((u) => (
                <tr key={u.id}>
                  <td>{u.id}</td><td>{u.name}</td><td>{u.email}</td><td>{formatDateTime(u.created_at)}</td>
                  <td><Button variant="outline" size="sm" onClick={() => setTarget(u)}>Delete</Button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <Pagination page={state.data?.page || 1} totalPages={state.data?.total_pages || 0} onChange={setPage} />
      </Section>
      <Modal open={Boolean(target)} title="Delete this account?" onClose={() => setTarget(null)}
        footer={<><Button variant="outline" onClick={() => setTarget(null)}>Keep it</Button><Button variant="danger" loading={busy} onClick={remove}>Yes, delete</Button></>}>
        {target && <p>{target.name} and everything they own (meals and reservations) will be removed.</p>}
      </Modal>
    </>
  );
}

function MealsTab() {
  const [page, setPage] = useState(1);
  const state = useFetch(() => api.getMeals({ page, limit: 10 }), [page]);
  const [target, setTarget] = useState(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });

  async function remove() {
    setBusy(true);
    try {
      await api.deleteMeal(target.id);
      setMessage({ type: "success", text: `"${target.name}" was removed.` });
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    } finally {
      setBusy(false);
      setTarget(null);
      state.reload();
    }
  }

  return (
    <>
      {message.text && <div className={`alert alert-${message.type}`} role="status">{message.text}</div>}
      <Section state={state}>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Meal</th><th>Provider</th><th>Category</th><th>Portions</th><th>Status</th><th></th></tr></thead>
            <tbody>
              {state.data?.items.map((m) => (
                <tr key={m.id}>
                  <td><Link to={`/meals/${m.id}`}>{m.name}</Link></td>
                  <td>{m.provider.name}</td><td>{m.category.name}</td><td>{m.quantity}</td>
                  <td><StatusBadge status={m.display_status} expiringSoon={m.expiring_soon} /></td>
                  <td><Button variant="outline" size="sm" onClick={() => setTarget(m)}>Remove</Button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <Pagination page={state.data?.page || 1} totalPages={state.data?.total_pages || 0} onChange={setPage} />
      </Section>
      <Modal open={Boolean(target)} title="Remove this listing?" onClose={() => setTarget(null)}
        footer={<><Button variant="outline" onClick={() => setTarget(null)}>Keep it</Button><Button variant="danger" loading={busy} onClick={remove}>Yes, remove</Button></>}>
        {target && <p>"{target.name}" by {target.provider.name} will be removed, along with its reservations.</p>}
      </Modal>
    </>
  );
}

function ReservationsTab() {
  const [page, setPage] = useState(1);
  const state = useFetch(() => api.providerReservations({ page, limit: 10 }), [page]);
  return (
    <Section state={state}>
      <div className="table-wrap">
        <table>
          <thead><tr><th>ID</th><th>Customer</th><th>Meal</th><th>Qty</th><th>Reserved</th><th>Status</th></tr></thead>
          <tbody>
            {state.data?.items.map((r) => (
              <tr key={r.id}>
                <td>{r.id}</td><td>{r.user.name}</td><td>{r.meal.name}</td><td>{r.quantity}</td>
                <td>{formatDateTime(r.reserved_at)}</td><td><StatusBadge status={r.display_status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Pagination page={state.data?.page || 1} totalPages={state.data?.total_pages || 0} onChange={setPage} />
    </Section>
  );
}

const TABS = ["Users", "Providers", "Meals", "Reservations"];

export default function AdminDashboard() {
  const stats = useFetch(() => api.adminStats(), []);
  const [tab, setTab] = useState("Users");
  const s = stats.data;

  return (
    <div className="container section">
      <h1>Admin dashboard</h1>
      {stats.loading && <LoadingSpinner label="Loading statistics..." />}
      {stats.error && <ErrorMessage message={stats.error} onRetry={stats.reload} />}
      {s && (
        <div className="stat-grid">
          <div className="stat"><strong>{s.total_users}</strong>Total users</div>
          <div className="stat"><strong>{s.total_providers}</strong>Total providers</div>
          <div className="stat"><strong>{s.total_meals}</strong>Total meals</div>
          <div className="stat"><strong>{s.active_meals}</strong>Active meals</div>
          <div className="stat"><strong>{s.total_reservations}</strong>Total reservations</div>
          <div className="stat"><strong>{s.collected_reservations}</strong>Collected</div>
        </div>
      )}

      <div className="tabs" role="tablist">
        {TABS.map((t) => (
          <button key={t} role="tab" aria-selected={tab === t} className={`tab ${tab === t ? "active" : ""}`} onClick={() => setTab(t)}>{t}</button>
        ))}
      </div>

      {tab === "Users" && <UsersTab role="USER" />}
      {tab === "Providers" && <UsersTab role="PROVIDER" />}
      {tab === "Meals" && <MealsTab />}
      {tab === "Reservations" && <ReservationsTab />}
    </div>
  );
}