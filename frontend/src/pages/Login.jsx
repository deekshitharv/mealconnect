import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import Button from "../components/Button";
import FormInput from "../components/FormInput";
import { useAuth } from "../hooks/useAuth";
import { homeFor } from "../utils/roles";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const user = await login(form.email.trim(), form.password);
      navigate(location.state?.from?.pathname || homeFor(user.role), { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="container section">
      <form className="card auth-card" onSubmit={onSubmit}>
        <h1>Welcome back</h1>
        <p className="muted">Log in to reserve meals or manage your listings.</p>
        {error && <div className="alert alert-error" role="alert">{error}</div>}
        <FormInput id="email" name="email" type="email" label="Email" autoComplete="email" required value={form.email} onChange={onChange} />
        <FormInput id="password" name="password" type="password" label="Password" autoComplete="current-password" required value={form.password} onChange={onChange} />
        <Button type="submit" loading={submitting} className="block">Log in</Button>
        <p className="muted small center">New here? <Link to="/register">Create an account</Link></p>
      </form>
    </div>
  );
}