import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { useUser } from "./context/UserContext";
import { ChatPage } from "./pages/Chat";
import { IngredientsPage } from "./pages/Ingredients";
import { ProfilePage } from "./pages/Profile";
import { RecipeDetailPage } from "./pages/RecipeDetail";
import { RecipesPage } from "./pages/Recipes";
import { SetupPage } from "./pages/Setup";
import { TodayPage } from "./pages/Today";

function RequireUser({ children }: { children: React.ReactNode }) {
  const { ready, userId } = useUser();
  if (!ready) {
    return <p className="boot">Loading…</p>;
  }
  if (!userId) {
    return <Navigate to="/setup" replace />;
  }
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/setup" element={<SetupPage />} />
      <Route
        element={
          <RequireUser>
            <Layout />
          </RequireUser>
        }
      >
        <Route path="/" element={<TodayPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/recipes" element={<RecipesPage />} />
        <Route path="/recipes/:recipeId" element={<RecipeDetailPage />} />
        <Route path="/ingredients" element={<IngredientsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Route>
    </Routes>
  );
}
