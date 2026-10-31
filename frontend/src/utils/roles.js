// Where each role lands after login.
export function homeFor(role) {
  if (role === "ADMIN") return "/admin/dashboard";
  if (role === "PROVIDER") return "/provider/dashboard";
  return "/dashboard";
}