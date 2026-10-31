import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";
import { toLocalInput } from "../utils/format";
import Button from "./Button";
import FormInput from "./FormInput";

// One form for both "add meal" and "edit meal". Pass `meal` to edit.
export default function MealForm({ meal, categories, locations }) {
  const navigate = useNavigate();
  const editing = Boolean(meal);

  const [form, setForm] = useState({
    name: meal?.name ?? "",
    category_id: meal ? String(meal.category.id) : "",
    description: meal?.description ?? "",
    location_id: meal ? String(meal.location.id) : "",
    quantity: meal ? String(meal.quantity) : "",
    available_from: toLocalInput(meal ? meal.available_from : new Date().toISOString()),
    available_until: meal ? toLocalInput(meal.available_until) : "",
    image_url: meal?.image_url ?? "",
    paused: meal?.status === "UNAVAILABLE",
  });
  const [newLoc, setNewLoc] = useState({ name: "", address: "", city: "" });
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
  const onLocChange = (e) => setNewLoc({ ...newLoc, [e.target.name]: e.target.value });

  function validate() {
    const e = {};
    if (form.name.trim().length < 2) e.name = "Enter at least 2 characters";
    if (!form.category_id) e.category_id = "Choose a category";
    if (!form.location_id) e.location_id = "Choose a location";
    if (form.location_id === "new") {
      if (newLoc.name.trim().length < 2) e.loc_name = "Enter a place name";
      if (newLoc.address.trim().length < 3) e.loc_address = "Enter an address";
      if (newLoc.city.trim().length < 2) e.loc_city = "Enter a city";
    }
    const qty = Number(form.quantity);
    const minQty = editing ? 0 : 1;
    if (form.quantity === "" || !Number.isInteger(qty) || qty < minQty || qty > 1000) {
      e.quantity = `Enter a whole number from ${minQty} to 1000`;
    }
    if (!form.available_from) e.available_from = "Choose a start time";
    if (!form.available_until) e.available_until = "Choose an end time";
    if (form.available_from && form.available_until) {
      if (new Date(form.available_until) <= new Date(form.available_from)) {
        e.available_until = "The end time must be after the start time";
      } else if (!editing && new Date(form.available_until) <= new Date()) {
        e.available_until = "The end time must be in the future";
      }
    }
    if (form.image_url.trim() && !/^https?:\/\//i.test(form.image_url.trim())) {
      e.image_url = "Must start with http:// or https://";
    }
    if (form.description.length > 1000) e.description = "Keep it under 1000 characters";
    return e;
  }

  async function onSubmit(ev) {
    ev.preventDefault();
    setFormError("");
    const found = validate();
    setErrors(found);
    if (Object.keys(found).length) return;

    setSubmitting(true);
    try {
      let locationId = Number(form.location_id);
      if (form.location_id === "new") {
        const created = await api.createLocation({
          name: newLoc.name.trim(),
          address: newLoc.address.trim(),
          city: newLoc.city.trim(),
        });
        locationId = created.id;
      }
      const payload = {
        name: form.name.trim(),
        description: form.description.trim() || null,
        category_id: Number(form.category_id),
        location_id: locationId,
        quantity: Number(form.quantity),
        available_from: new Date(form.available_from).toISOString(),
        available_until: new Date(form.available_until).toISOString(),
        image_url: form.image_url.trim() || null,
      };
      if (editing) {
        payload.status = form.paused ? "UNAVAILABLE" : "AVAILABLE";
        await api.updateMeal(meal.id, payload);
      } else {
        await api.createMeal(payload);
      }
      navigate("/provider/dashboard", { state: { notice: editing ? "Meal updated." : "Meal created. It is now visible to everyone." } });
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="card form-card" onSubmit={onSubmit} noValidate>
      <h1>{editing ? "Edit meal" : "Add a meal"}</h1>
      {formError && <div className="alert alert-error" role="alert">{formError}</div>}

      <div className="form-grid">
        <div className="span-2">
          <FormInput id="name" name="name" label="Meal name" value={form.name} onChange={onChange} error={errors.name} maxLength={150} />
        </div>

        <FormInput as="select" id="category_id" name="category_id" label="Category" value={form.category_id} onChange={onChange} error={errors.category_id}>
          <option value="">Choose...</option>
          {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </FormInput>

        <FormInput as="select" id="location_id" name="location_id" label="Location" value={form.location_id} onChange={onChange} error={errors.location_id}>
          <option value="">Choose...</option>
          {locations.map((l) => <option key={l.id} value={l.id}>{l.name}, {l.city}</option>)}
          <option value="new">+ Add a new location</option>
        </FormInput>

        {form.location_id === "new" && (
          <>
            <FormInput id="loc_name" name="name" label="Place name" value={newLoc.name} onChange={onLocChange} error={errors.loc_name} />
            <FormInput id="loc_city" name="city" label="City" value={newLoc.city} onChange={onLocChange} error={errors.loc_city} />
            <div className="span-2">
              <FormInput id="loc_address" name="address" label="Address" value={newLoc.address} onChange={onLocChange} error={errors.loc_address} />
            </div>
          </>
        )}

        <div className="span-2">
          <FormInput as="textarea" rows={3} id="description" name="description" label="Description" value={form.description} onChange={onChange} error={errors.description} />
        </div>

        <FormInput id="quantity" name="quantity" type="number" min={editing ? 0 : 1} max={1000} label="Quantity (portions)" value={form.quantity} onChange={onChange} error={errors.quantity} />
        <FormInput id="image_url" name="image_url" type="url" label="Image URL (optional)" placeholder="https://..." value={form.image_url} onChange={onChange} error={errors.image_url} />

        <FormInput id="available_from" name="available_from" type="datetime-local" label="Available from" value={form.available_from} onChange={onChange} error={errors.available_from} />
        <FormInput id="available_until" name="available_until" type="datetime-local" label="Available until" value={form.available_until} onChange={onChange} error={errors.available_until} />
      </div>

      {editing && (
        <label className="checkbox">
          <input type="checkbox" checked={form.paused} onChange={(e) => setForm({ ...form, paused: e.target.checked })} />
          Pause this listing (hide it from reservations)
        </label>
      )}

      <div className="form-actions">
        <Button type="submit" loading={submitting}>{editing ? "Save changes" : "Create meal"}</Button>
        <Button variant="outline" onClick={() => navigate("/provider/dashboard")}>Cancel</Button>
      </div>
    </form>
  );
}