export default function EmptyState({ title, text, action }) {
  return (
    <div className="empty">
      <div className="empty-icon">🍽️</div>
      <h3>{title}</h3>
      {text && <p className="muted">{text}</p>}
      {action}
    </div>
  );
}