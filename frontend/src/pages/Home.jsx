import { Link } from "react-router-dom";
import ErrorMessage from "../components/ErrorMessage";
import LoadingSpinner from "../components/LoadingSpinner";
import MealGrid from "../components/MealGrid";
import { useAuth } from "../hooks/useAuth";
import useFetch from "../hooks/useFetch";
import { api } from "../services/api";
import { homeFor } from "../utils/roles";

const FEATURES = [
  ["♻️", "Reduce food waste", "Good food that would be thrown away finds a hungry home instead."],
  ["🤝", "Help your community", "Neighbours, students and families share what is left over."],
  ["👆", "Simple & easy", "Browse, reserve a portion, and collect it in person."],
  ["🌱", "A greener future", "Every shared meal is a small step toward less waste."],
];

export default function Home() {
  const { user } = useAuth();
  const latest = useFetch(() => api.getMeals({ status: "AVAILABLE", sort: "expiry", limit: 3 }), []);

  return (
    <>
      <section className="hero">
        <div className="container hero-inner">
          <h1>Connect. Share. Enjoy.</h1>
          <p>Find and reserve available meals near you.</p>
          <div className="hero-actions">
            <Link to="/meals" className="btn btn-primary btn-lg">Browse Meals</Link>
            <Link to={user ? homeFor(user.role) : "/register"} className="btn btn-green btn-lg">
              {user ? "My dashboard" : "Get Started"}
            </Link>
          </div>
        </div>
      </section>

      <section className="container section">
        <div className="feature-grid">
          {FEATURES.map(([icon, title, text]) => (
            <div className="card feature" key={title}>
              <div className="feature-icon">{icon}</div>
              <h3>{title}</h3>
              <p className="muted">{text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="container section">
        <div className="section-head">
          <h2>Ending soon</h2>
          <Link to="/meals?sort=expiry">See all meals</Link>
        </div>
        {latest.loading && <LoadingSpinner label="Finding meals..." />}
        {latest.error && <ErrorMessage message={latest.error} onRetry={latest.reload} />}
        {latest.data && latest.data.items.length === 0 && <p className="muted">No meals are available right now. Check back soon.</p>}
        {latest.data && latest.data.items.length > 0 && <MealGrid meals={latest.data.items} />}
      </section>
    </>
  );
}