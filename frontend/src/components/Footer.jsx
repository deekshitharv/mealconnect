import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <p><strong>MealConnect</strong> | Food Sharing &amp; Reservation System</p>
        <p className="muted small">
          <Link to="/how-it-works">How it works</Link> · <Link to="/about">About</Link> · Collect in person. No delivery, no payment.
        </p>
      </div>
    </footer>
  );
}