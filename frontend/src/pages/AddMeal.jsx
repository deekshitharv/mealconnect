import ErrorMessage from "../components/ErrorMessage";
import LoadingSpinner from "../components/LoadingSpinner";
import MealForm from "../components/MealForm";
import useFetch from "../hooks/useFetch";
import { api } from "../services/api";

export default function AddMeal() {
  const categories = useFetch(() => api.getCategories(), []);
  const locations = useFetch(() => api.getLocations(), []);

  return (
    <div className="container section">
      {(categories.loading || locations.loading) && <LoadingSpinner label="Loading form..." />}
      {(categories.error || locations.error) && (
        <ErrorMessage message={categories.error || locations.error} onRetry={() => { categories.reload(); locations.reload(); }} />
      )}
      {categories.data && locations.data && <MealForm categories={categories.data} locations={locations.data} />}
    </div>
  );
}