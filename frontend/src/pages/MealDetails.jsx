import { useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import Button from "../components/Button";
import ErrorMessage from "../components/ErrorMessage";
import LoadingSpinner from "../components/LoadingSpinner";
import StatusBadge from "../components/StatusBadge";
import { useAuth } from "../hooks/useAuth";
import useFetch from "../hooks/useFetch";
import { api } from "../services/api";
import { formatDateTime, timeLeft } from "../utils/format";

export default function MealDetails() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { data: meal, loading, error, reload } = useFetch(() => api.getMeal(id), [id]);
  const [quantity, setQuantity] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [reserveError, setReserveError] = useState("");

  if (loading) return <LoadingSpinner label="Loading meal..." />;
  if (error) {
    return (
      <div className="container section">
        <ErrorMessage message={error} onRetry={reload} />
        <Link to="/meals">Back to all meals</Link>
      </div>
    );
  }

  const notStarted = new Date(meal.available_from) > new Date();
  const isOwner = user && user.id === meal.provider.id;
  const canReserve = meal.display_status === "AVAILABLE" && meal.quantity > 0 && !notStarted;
  const maxQty = Math.min(meal.quantity, 100);

  async function reserve() {
    setReserveError("");
    setSubmitting(true);
    try {
      const reservation = await api.reserve(meal.id, quantity);
      navigate(`/reservation-success/${reservation.id}`);
    } catch (err) {
      setReserveError(err.message);
      reload(); // the meal may have changed (someone else reserved first)
    } finally {
      setSubmitting(false);
    }
  }

  let action;
  if (!canReserve) {
    const reason =
      meal.display_status === "EXPIRED" ? "This meal has expired"
      : meal.display_status === "FULLY_RESERVED" ? "Fully reserved"
      : notStarted ? `Available from ${formatDateTime(meal.available_from)}`
      : "Not available";
    action = <Button disabled className="block">{reason}</Button>;
  } else if (!user) {
    action = (
      <Link to="/login" state={{ from: location }} className="btn btn-primary btn-md block">
        Login to Reserve
      </Link>
    );
  } else if (isOwner) {
    action = <Button disabled className="block">This is your listing</Button>;
  } else {
    action = (
      <>
        <label className="qty-label" htmlFor="qty">Portions</label>
        <div className="qty">
          <Button variant="outline" size="sm" aria-label="Fewer" disabled={quantity <= 1} onClick={() => setQuantity(quantity - 1)}>−</Button>
          <input id="qty" className="input qty-input" type="number" min={1} max={maxQty} value={quantity}
            onChange={(e) => setQuantity(Math.max(1, Math.min(maxQty, Number(e.target.value) || 1)))} />
          <Button variant="outline" size="sm" aria-label="More" disabled={quantity >= maxQty} onClick={() => setQuantity(quantity + 1)}>+</Button>
        </div>
        <Button loading={submitting} className="block" onClick={reserve}>Reserve</Button>
      </>
    );
  }

  return (
    <div className="container section">
      <Link to="/meals">← Back to meals</Link>
      <div className="details">
        <div className="details-image">
          {meal.image_url ? <img src={meal.image_url} alt={meal.name} /> : <span className="placeholder big">🍽️</span>}
        </div>
        <div className="card details-body">
          <div className="meal-top">
            <span className="tag">{meal.category.name}</span>
            <StatusBadge status={meal.display_status} expiringSoon={meal.expiring_soon} />
          </div>
          <h1>{meal.name}</h1>
          <p>{meal.description || "No description provided."}</p>
          <ul className="meta">
            <li>🏪 Provider: {meal.provider.name}</li>
            <li>📍 {meal.location.name}, {meal.location.address}, {meal.location.city}</li>
            <li>🍱 <strong>{meal.quantity}</strong> portion{meal.quantity === 1 ? "" : "s"} available</li>
            <li>⏰ Pick up before {formatDateTime(meal.available_until)} ({timeLeft(meal.available_until)})</li>
          </ul>
          {reserveError && <div className="alert alert-error" role="alert">{reserveError}</div>}
          <div className="reserve-box">{action}</div>
        </div>
      </div>
    </div>
  );
}