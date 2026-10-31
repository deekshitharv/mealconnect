import { useEffect, useState } from "react";
import Button from "./Button";

export default function SearchBar({ value, onSearch, placeholder = "Search meals, e.g. rice" }) {
  const [text, setText] = useState(value);
  useEffect(() => setText(value), [value]);

  return (
    <form
      className="searchbar"
      role="search"
      onSubmit={(e) => {
        e.preventDefault();
        onSearch(text.trim());
      }}
    >
      <input
        className="input"
        type="search"
        value={text}
        placeholder={placeholder}
        aria-label="Search meals"
        onChange={(e) => setText(e.target.value)}
      />
      <Button type="submit">Search</Button>
    </form>
  );
}