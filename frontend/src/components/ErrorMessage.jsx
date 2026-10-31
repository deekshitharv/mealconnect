import Button from "./Button";

export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="alert alert-error" role="alert">
      <span>{message || "Something went wrong."}</span>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  );
}