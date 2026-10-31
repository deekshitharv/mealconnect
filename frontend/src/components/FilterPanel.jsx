import Button from "./Button";
import FormInput from "./FormInput";

export default function FilterPanel({ filters, categories, cities, onChange }) {
  return (
    <div className="filters">
      <FormInput as="select" id="f-category" label="Category" value={filters.category}
        onChange={(e) => onChange({ category: e.target.value })}>
        <option value="">All categories</option>
        {categories.map((c) => (
          <option key={c.id} value={c.name}>{c.name}</option>
        ))}
      </FormInput>

      <FormInput as="select" id="f-location" label="Location" value={filters.location}
        onChange={(e) => onChange({ location: e.target.value })}>
        <option value="">All locations</option>
        {cities.map((city) => (
          <option key={city} value={city}>{city}</option>
        ))}
      </FormInput>

      <FormInput as="select" id="f-status" label="Status" value={filters.status}
        onChange={(e) => onChange({ status: e.target.value })}>
        <option value="">Any status</option>
        <option value="AVAILABLE">Available</option>
        <option value="FULLY_RESERVED">Fully reserved</option>
        <option value="EXPIRED">Expired</option>
      </FormInput>

      <FormInput as="select" id="f-sort" label="Sort by" value={filters.sort}
        onChange={(e) => onChange({ sort: e.target.value })}>
        <option value="newest">Newest</option>
        <option value="expiry">Ending soonest</option>
        <option value="quantity">Most portions</option>
      </FormInput>

      <div className="field field-action">
        <Button variant="ghost" onClick={() => onChange({ category: "", location: "", status: "", sort: "newest", search: "" })}>
          Clear filters
        </Button>
      </div>
    </div>
  );
}