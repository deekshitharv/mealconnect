import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { homeFor } from "../utils/roles";
import Button from "./Button";

export default function Navbar() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const close = () => setOpen(false);

  function handleLogout() {
    logout();
    close();
    navigate("/");
  }

  return (
    <header className="navbar">
      <div className="container nav-inner">
        <Link to="/" className="brand" onClick={close}>
          🍽️ Meal<span>Connect</span>
        </Link>
        <button className="nav-toggle" aria-label="Toggle menu" aria-expanded={open} onClick={() => setOpen(!open)}>
          {open ? "✕" : "☰"}
        </button>
        <nav className={`nav-links ${open ? "open" : ""}`}>
          <NavLink to="/meals" onClick={close}>Browse meals</NavLink>
          <NavLink to="/how-it-works" onClick={close}>How it works</NavLink>
          <NavLink to="/about" onClick={close}>About</NavLink>
          {user ? (
            <>
              <NavLink to={homeFor(user.role)} onClick={close}>Dashboard</NavLink>
              <span className="nav-user">{user.name}</span>
              <Button variant="ghost" size="sm" onClick={handleLogout}>Logout</Button>
            </>
          ) : (
            <>
              <NavLink to="/login" onClick={close}>Login</NavLink>
              <Link to="/register" className="btn btn-primary btn-sm" onClick={close}>Get started</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}