import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import ProductList from './components/ProductList';
import ProductForm from './components/ProductForm';
import ProductDetail from './components/ProductDetail';
import './App.css';

function NavBar() {
  const loc = useLocation();
  return (
    <nav className="navbar">
      <div className="nav-brand">
        <div className="brand-icon">🔁</div>
        <div>
          <span>DevLoop</span>
          <span className="brand-sub">Product Management</span>
        </div>
      </div>
      <div className="nav-actions">
        <Link to="/" className={`nav-link ${loc.pathname === '/' ? 'active' : ''}`}>
          📋 Products
        </Link>
        <Link to="/products/new" className="nav-link primary-link">
          ＋ New Product
        </Link>
      </div>
    </nav>
  );
}

function App() {
  return (
    <BrowserRouter>
      <NavBar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<ProductList />} />
          <Route path="/products/new" element={<ProductForm />} />
          <Route path="/products/:id" element={<ProductDetail />} />
          <Route path="/products/:id/edit" element={<ProductForm />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;
