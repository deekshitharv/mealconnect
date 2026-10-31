import { useSearchParams } from "react-router-dom";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import FilterPanel from "../components/FilterPanel";
import LoadingSpinner from "../components/LoadingSpinner";
import MealGrid from "../components/MealGrid";
import Pagination from "../components/Pagination";
import SearchBar from "../components/SearchBar";
import useFetch from "../hooks/useFetch";
import { api } from "../services/api";

export default function Browse() {
  // Filters live in the URL (?category=Lunch&page=2), so the back button and shared links work.
  const [params, setParams] = useSearchParams();
  const filters = {
    search: params.get("search") || "",
    category: params.get("category") || "",
    location: params.get("location") || "",
    status: params.get("status") || "",
    sort: params.get("sort") || "newest",
    page: Number(params.get("page")) || 1,
  };

  function setFilters(changes) {
    const next = { ...filters, page: 1, ...changes }; // changing a filter goes back to page 1
    const clean = {};
    Object.entries(next).forEach(([key, value]) => {
      const isDefault = (key === "page" && value === 1) || (key === "sort" && value === "newest");
      if (value && !isDefault) clean[key] = String(value);
    });
    setParams(clean);
  }

  const categories = useFetch(() => api.getCategories(), []);
  const locations = useFetch(() => api.getLocations(), []);
  const meals = useFetch(() => api.getMeals({ ...filters, limit: 9 }), [params.toString()]);

  const cities = [...new Set((locations.data || []).map((l) => l.city))];

  return (
    <div className="container section">
      <h1>Browse meals</h1>
      <p className="muted">Fresh listings from restaurants, cafes, caterers and community kitchens.</p>

      <SearchBar value={filters.search} onSearch={(search) => setFilters({ search })} />
      <FilterPanel filters={filters} categories={categories.data || []} cities={cities} onChange={setFilters} />

      {meals.loading && <LoadingSpinner label="Loading meals..." />}
      {meals.error && <ErrorMessage message={meals.error} onRetry={meals.reload} />}

      {meals.data && (
        <>
          <p className="muted small">{meals.data.total} meal{meals.data.total === 1 ? "" : "s"} found</p>
          {meals.data.items.length === 0 ? (
            <EmptyState title="No meals match your search" text="Try a different word, or clear the filters." />
          ) : (
            <MealGrid meals={meals.data.items} />
          )}
          <Pagination page={meals.data.page} totalPages={meals.data.total_pages} onChange={(page) => setFilters({ page })} />
        </>
      )}
    </div>
  );
}