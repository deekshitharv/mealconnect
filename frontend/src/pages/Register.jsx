import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Button from "../components/Button";
import FormInput from "../components/FormInput";
import { useAuth } from "../hooks/useAuth";
import { homeFor } from "../utils/roles";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "USER" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const user = await register({ ...form, name: form.name.trim(), email: form.email.trim() });
      navigate(homeFor(user.role), { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="container section">
      <form className="card auth-card" onSubmit={onSubmit}>
        <h1>Create your account</h1>
        <p className="muted">It takes a minute.</p>
        {error && <div className="alert alert-error" role="alert">{error}</div>}
        <FormInput id="name" name="name" label="Full name" autoComplete="name" required minLength={2} value={form.name} onChange={onChange} />
        <FormInput id="email" name="email" type="email" label="Email" autoComplete="email" required value={form.email} onChange={onChange} />
        <FormInput id="password" name="password" type="password" label="Password" autoComplete="new-password" required minLength={8} maxLength={72} hint="At least 8 characters" value={form.password} onChange={onChange} />
        <FormInput as="select" id="role" name="role" label="I want to" value={form.role} onChange={onChange}>
          <option value="USER">Find and reserve meals</option>
          <option value="PROVIDER">Share food as a provider</option>
        </FormInput>
        <Button type="submit" loading={submitting} className="block">Create account</Button>
        <p className="muted small center">Already registered? <Link to="/login">Log in</Link></p>
      </form>
    </div>
  );
}