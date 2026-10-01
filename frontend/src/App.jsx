import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth.jsx";
import Layout from "./components/Layout.jsx";
import Courses from "./pages/Courses.jsx";
import Inbox from "./pages/Inbox.jsx";
import SignIn from "./pages/SignIn.jsx";

function RequireAuth({ children }) {
  const { token } = useAuth();
  return token ? children : <Navigate to="/signin" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/signin" element={<SignIn />} />
      <Route
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
        <Route index element={<Inbox />} />
        <Route path="courses" element={<Courses />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
