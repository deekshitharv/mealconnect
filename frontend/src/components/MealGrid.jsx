import MealCard from "./MealCard";

export default function MealGrid({ meals }) {
  return (
    <div className="meal-grid">
      {meals.map((meal) => (
        <MealCard key={meal.id} meal={meal} />
      ))}
    </div>
  );
}