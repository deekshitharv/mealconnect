const STEPS = [
  ["1", "Discover", "Browse meals shared near you, or search by name, category and location."],
  ["2", "Choose", "Open a meal to see the portions left, the pick-up place and the deadline."],
  ["3", "Reserve", "Pick how many portions you need. The count updates straight away."],
  ["4", "Collect", "Go to the pick-up place before the deadline and collect your food."],
];
const PROVIDER = [
  "Register as a provider.",
  "List the food you have to share, with a quantity and a pick-up deadline.",
  "Watch reservations arrive on your dashboard.",
  "Mark each reservation as collected when the person picks it up.",
];

export default function HowItWorks() {
  return (
    <div className="container section">
      <h1>How it works</h1>
      <p className="muted">MealConnect is for sharing food in person. There is no delivery and no payment.</p>
      <div className="feature-grid">
        {STEPS.map(([n, title, text]) => (
          <div className="card feature" key={n}>
            <div className="step-number">{n}</div>
            <h3>{title}</h3>
            <p className="muted">{text}</p>
          </div>
        ))}
      </div>
      <h2 className="gap-top">For food providers</h2>
      <div className="card">
        <ol className="plain-list">
          {PROVIDER.map((text) => <li key={text}>{text}</li>)}
        </ol>
      </div>
    </div>
  );
}