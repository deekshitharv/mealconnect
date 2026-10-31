import { useEffect, useState } from "react";

// Runs an API call and gives back { data, loading, error, reload }.
// Pass the values the call depends on as `deps`, and it re-runs when they change.
export default function useFetch(fetcher, deps = []) {
  const [state, setState] = useState({ data: null, loading: true, error: "" });
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let cancelled = false; // ignore answers that arrive after we have moved on
    setState((s) => ({ ...s, loading: true, error: "" }));
    fetcher()
      .then((data) => {
        if (!cancelled) setState({ data, loading: false, error: "" });
      })
      .catch((err) => {
        if (!cancelled) setState({ data: null, loading: false, error: err.message });
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);

  return { ...state, reload: () => setTick((t) => t + 1) };
}