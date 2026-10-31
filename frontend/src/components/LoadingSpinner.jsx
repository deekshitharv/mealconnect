export default function LoadingSpinner({ label = "Loading..." }) {
  return (
    <div className="center-block" role="status">
      <div className="spinner" />
      <p className="muted">{label}</p>
    </div>
  );
}