// src/App.jsx - Updated with Campaigns Route
import React, { useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import useAuth from "./hooks/useAuth";
import AuthModal from "./components/AuthModal";
import AppLayout from "./components/layout/AppLayout";

// Import existing pages
import UserDashboard from "./pages/UserDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import OwnerDashboard from "./pages/OwnerDashboard";
import FormSubmitterPage from "./pages/FormSubmitterPage";
import ContactInformationForm from "./pages/ContactInformationForm";
import CampaignDetailPage from "./pages/CampaignDetailPage";
import LandingPage from "./pages/LandingPage";
import DashboardPage from "./pages/DashboardPage";

// Import new Campaigns page
import CampaignsPage from "./pages/CampaignsPage";

const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { user } = useAuth();
  
  if (!user) return <Navigate to="/" replace />;
  
  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
};

const App = () => {
  const { user, loading, login, register } = useAuth();
  const [showModal, setShowModal] = useState(false);
  const [view, setView] = useState("login");

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const openModal = (type) => {
    setView(type);
    setShowModal(true);
  };

  return (
    <>
      <Toaster
        position="top-center"
        toastOptions={{
          duration: 5000,
          style: {
            padding: "16px",
            fontSize: "14px",
            maxWidth: "500px",
            background: "#ffffff",
            color: "#1f2937",
            border: "1px solid #e5e7eb",
            borderRadius: "8px",
            boxShadow: "0 10px 25px rgba(0,0,0,0.1)",
          },
          success: {
            iconTheme: {
              primary: "#10b981",
              secondary: "#ffffff",
            },
            style: {
              background: "#f0fdf4",
              color: "#166534",
              border: "1px solid #86efac",
            },
          },
          error: {
            iconTheme: {
              primary: "#ef4444",
              secondary: "#ffffff",
            },
            style: {
              background: "#fef2f2",
              color: "#991b1b",
              border: "1px solid #fca5a5",
            },
            duration: 6000,
          },
        }}
      />

      <Routes>
        <Route element={<AppLayout />}>
          <Route
            index
            element={
              <LandingPage
                onLogin={() => openModal("login")}
                onRegister={() => openModal("register")}
              />
            }
          />

          {/* Main dashboard - renders based on user role */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />

          {/* NEW: Campaigns list page */}
          <Route
            path="/campaigns"
            element={
              <ProtectedRoute>
                <CampaignsPage />
              </ProtectedRoute>
            }
          />
          
          {/* Individual campaign detail */}
          <Route
            path="/campaigns/:campaignId"
            element={
              <ProtectedRoute>
                <CampaignDetailPage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/contact-info"
            element={
              <ProtectedRoute>
                <ContactInformationForm />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/ContactInformationForm"
            element={
              <ProtectedRoute>
                <ContactInformationForm />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/form-submitter"
            element={
              <ProtectedRoute>
                <FormSubmitterPage />
              </ProtectedRoute>
            }
          />

          {/* User specific routes */}
          <Route
            path="/user"
            element={
              <ProtectedRoute allowedRoles={["user"]}>
                <UserDashboard />
              </ProtectedRoute>
            }
          />

          {/* Admin specific routes */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          
          {/* Owner specific routes */}
          <Route
            path="/owner"
            element={
              <ProtectedRoute allowedRoles={["owner"]}>
                <OwnerDashboard />
              </ProtectedRoute>
            }
          />

          {/* Catch all - redirect to home */}
          <Route path="*" element={<Navigate to="/" />} />
        </Route>
      </Routes>

      <AuthModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        view={view}
        onSwitchView={setView}
        onLogin={login}
        onRegister={register}
      />
    </>
  );
};

export default App;