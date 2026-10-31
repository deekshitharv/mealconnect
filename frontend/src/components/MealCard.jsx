import { Link } from "react-router-dom";
import { formatDateTime } from "../utils/format";
import StatusBadge from "./StatusBadge";

export default function MealCard({ meal }) {
  return (
    <article className="card meal-card">
      <Link to={`/meals/${meal.id}`} className="meal-image" aria-label={meal.name}>
        {meal.image_url ? (
          <img
            src={meal.image_url}
            alt={meal.name}
            loading="lazy"
            onError={(e) => {
              e.currentTarget.style.display = "none";
            }}
          />
        ) : (
          <span className="placeholder">🍽️</span>
        )}
      </Link>
      <div className="meal-body">
        <div className="meal-top">
          <span className="tag">{meal.category.name}</span>
          <StatusBadge status={meal.display_status} expiringSoon={meal.expiring_soon} />
        </div>
        <h3>{meal.name}</h3>
        <p className="muted small">by {meal.provider.name}</p>
        <ul className="meta">
          <li>📍 {meal.location.name}, {meal.location.city}</li>
          <li>🍱 {meal.quantity} portion{meal.quantity === 1 ? "" : "s"} left</li>
          <li>⏰ Until {formatDateTime(meal.available_until)}</li>
        </ul>
        <Link to={`/meals/${meal.id}`} className="btn btn-outline btn-md block">
          View details
        </Link>
      </div>
    </article>
  );
}