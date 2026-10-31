import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="container section center">
      <h1>Page not found</h1>
      <p className="muted">That page does not exist.</p>
      <Link to="/" className="btn btn-primary btn-md">Go home</Link>
    </div>
  );
}