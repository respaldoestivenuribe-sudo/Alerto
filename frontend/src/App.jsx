import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { ResetPassword } from './pages/ResetPassword'
import { Precipitation } from './pages/Precipitation'
import { Risk } from './pages/Risk'
import { Simulator } from './pages/Simulator'
import { Alerts } from './pages/Alerts'
import { Admin } from './pages/Admin'
import { isAuthenticated, isAdmin } from './utils/auth'

const ProtectedRoute = ({ children }) =>
  isAuthenticated() ? children : <Navigate to="/login" replace />

const AdminRoute = ({ children }) =>
  isAuthenticated() && isAdmin() ? children : <Navigate to="/precipitation" replace />

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login"          element={<Login />} />
        <Route path="/register"       element={<Register />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route path="precipitation" element={<Precipitation />} />
          <Route path="risk"          element={<Risk />} />
          <Route path="simulator"     element={<Simulator />} />
          <Route path="alerts"        element={<Alerts />} />
          <Route path="admin"         element={<AdminRoute><Admin /></AdminRoute>} />
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
