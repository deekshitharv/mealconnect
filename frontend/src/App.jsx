import { useEffect, useState } from "react";
import { checkHealth } from "./services/api";

function App() {
  const [status, setStatus] = useState("checking...");
  const [error, setError] = useState("");

  useEffect(() => {
    checkHealth()
      .then((data) => setStatus(data.status))
      .catch((err) => {
        setStatus("unreachable");
        setError(err.message);
      });
  }, []);

  return (
    <main style={{ textAlign: "center", padding: "2rem" }}>
      <h1>🍽️ MealConnect</h1>
      <p>Food Sharing &amp; Reservation System</p>
      <h2>API status: {status}</h2>
      {error && <p style={{ color: "#d9480f" }}>Error: {error}</p>}
    </main>
  );
}

export default App;
