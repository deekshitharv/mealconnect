import { Outlet, Route, Routes } from "react-router-dom";
import Footer from "./components/Footer";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import RoleProtectedRoute from "./components/RoleProtectedRoute";
import About from "./pages/About";
import AddMeal from "./pages/AddMeal";
import AdminDashboard from "./pages/AdminDashboard";
import Browse from "./pages/Browse";
import EditMeal from "./pages/EditMeal";
import Home from "./pages/Home";
import HowItWorks from "./pages/HowItWorks";
import Login from "./pages/Login";
import MealDetails from "./pages/MealDetails";
import NotFound from "./pages/NotFound";
import ProviderDashboard from "./pages/ProviderDashboard";
import ProviderReservations from "./pages/ProviderReservations";
import Register from "./pages/Register";
import ReservationSuccess from "./pages/ReservationSuccess";
import UserDashboard from "./pages/UserDashboard";

function Layout() {
  return (
    <div className="app">
      <Navbar />
      <main className="main">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}

const only = (roles, page) => <RoleProtectedRoute roles={roles}>{page}</RoleProtectedRoute>;

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/meals" element={<Browse />} />
        <Route path="/meals/:id" element={<MealDetails />} />
        <Route path="/how-it-works" element={<HowItWorks />} />
        <Route path="/about" element={<About />} />

        <Route path="/reservation-success/:id" element={<ProtectedRoute><ReservationSuccess /></ProtectedRoute>} />
        <Route path="/dashboard" element={only(["USER"], <UserDashboard />)} />

        <Route path="/provider/dashboard" element={only(["PROVIDER"], <ProviderDashboard />)} />
        <Route path="/provider/meals/new" element={only(["PROVIDER"], <AddMeal />)} />
        <Route path="/provider/meals/:id/edit" element={only(["PROVIDER"], <EditMeal />)} />
        <Route path="/provider/reservations" element={only(["PROVIDER"], <ProviderReservations />)} />

        <Route path="/admin/dashboard" element={only(["ADMIN"], <AdminDashboard />)} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}