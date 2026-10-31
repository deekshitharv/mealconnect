import { Link, useParams } from "react-router-dom";
import ErrorMessage from "../components/ErrorMessage";
import LoadingSpinner from "../components/LoadingSpinner";
import MealForm from "../components/MealForm";
import { useAuth } from "../hooks/useAuth";
import useFetch from "../hooks/useFetch";
import { api } from "../services/api";

export default function EditMeal() {
  const { id } = useParams();
  const { user } = useAuth();
  const meal = useFetch(() => api.getMeal(id), [id]);
  const categories = useFetch(() => api.getCategories(), []);
  const locations = useFetch(() => api.getLocations(), []);

  const loading = meal.loading || categories.loading || locations.loading;
  const error = meal.error || categories.error || locations.error;

  return (
    <div className="container section">
      {loading && <LoadingSpinner label="Loading meal..." />}
      {error && <ErrorMessage message={error} onRetry={() => { meal.reload(); categories.reload(); locations.reload(); }} />}
      {meal.data && meal.data.provider.id !== user.id && (
        <>
          <ErrorMessage message="You can only edit your own meals." />
          <Link to="/provider/dashboard">Back to dashboard</Link>
        </>
      )}
      {meal.data && meal.data.provider.id === user.id && categories.data && locations.data && (
        <MealForm meal={meal.data} categories={categories.data} locations={locations.data} />
      )}
    </div>
  );
}