import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { productApi } from '../services/api';

const CATEGORIES = ['ALL', 'ELECTRONICS', 'FURNITURE', 'STATIONERY'];

const CAT_ICONS = { ALL: '🗂️', ELECTRONICS: '💻', FURNITURE: '🪑', STATIONERY: '✏️' };

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteError, setDeleteError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    let active = true;
    const loadProducts = async () => {
      try {
        setLoading(true);
        const res = await productApi.getAll(selectedCategory !== 'ALL' ? selectedCategory : null);
        if (active) setProducts(res.data);
      } catch {
        if (active) setError('Failed to load products. Is the backend running?');
      } finally {
        if (active) setLoading(false);
      }
    };
    loadProducts();
    return () => { active = false; };
  }, [selectedCategory]);

  const handleDelete = async (id, name) => {
    setDeleteError(null);
    if (!window.confirm(`Delete "${name}"? This cannot be undone.`)) return;
    try {
      await productApi.delete(id);
      setProducts(products.filter((p) => p.id !== id));
    } catch {
      setDeleteError(`Failed to delete product "${name}"`);
    }
  };

  const filtered = products.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.sku.toLowerCase().includes(search.toLowerCase())
  );

  const stats = {
    total: products.length,
    active: products.filter((p) => p.status === 'ACTIVE').length,
    lowStock: products.filter((p) => p.stock < 10).length,
    categories: [...new Set(products.map((p) => p.category))].length,
  };

  if (loading) return (
    <div className="loading-wrap">
      <div className="spinner" />
      <span className="loading-text">Loading products…</span>
    </div>
  );

  if (error) return (
    <div className="error-box">⚠️ {error}</div>
  );

  return (
    <div className="product-list">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h2>Products</h2>
          <p>{products.length} items in inventory</p>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="stats-bar">
        <div className="stat-card">
          <div className="stat-icon blue">📦</div>
          <div>
            <div className="stat-val">{stats.total}</div>
            <div className="stat-label">Total Products</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon green">✅</div>
          <div>
            <div className="stat-val">{stats.active}</div>
            <div className="stat-label">Active</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon amber">⚠️</div>
          <div>
            <div className="stat-val">{stats.lowStock}</div>
            <div className="stat-label">Low Stock</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon red">🗂️</div>
          <div>
            <div className="stat-val">{stats.categories}</div>
            <div className="stat-label">Categories</div>
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className="toolbar">
        <div className="search-wrap">
          <span className="search-icon">🔍</span>
          <input
            className="search-input"
            placeholder="Search by name or SKU…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="category-filters">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              className={`filter-btn ${selectedCategory === cat ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat)}
            >
              {CAT_ICONS[cat]} {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Deletion Error notification */}
      {deleteError && (
        <div className="delete-error">
          <span>⚠️ {deleteError}</span>
          <button onClick={() => setDeleteError(null)} className="delete-error-close">✕</button>
        </div>
      )}

      {/* Total product count label */}
      <div className="product-count">
        Showing {filtered.length} {filtered.length === 1 ? 'product' : 'products'}
      </div>

      {/* Table */}
      <div className="table-wrap">
        <table className="product-table">
          <thead>
            <tr>
              <th>SKU</th>
              <th>Name</th>
              <th>Category</th>
              <th>Price</th>
              <th>Stock</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((p) => (
              <tr key={p.id} className={p.stock < 10 ? 'low-stock-row' : ''}>
                <td><span className="sku-chip">{p.sku}</span></td>
                <td>
                  <Link to={`/products/${p.id}`} className="product-name-link">
                    {p.name}
                  </Link>
                </td>
                <td>{CAT_ICONS[p.category]} {p.category}</td>
                <td><strong>${parseFloat(p.price).toFixed(2)}</strong></td>
                <td>
                  {p.stock < 10
                    ? <span className="stock-warning">⚠️ {p.stock}</span>
                    : <span className="stock-ok">{p.stock}</span>
                  }
                </td>
                <td>
                  <span className={`status-badge status-${p.status?.toLowerCase()}`}>
                    {p.status}
                  </span>
                </td>
                <td>
                  <div className="action-cell">
                    <button onClick={() => navigate(`/products/${p.id}/edit`)} className="btn btn-edit">✏️ Edit</button>
                    <button onClick={() => handleDelete(p.id, p.name)} className="btn btn-delete">🗑️</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filtered.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <div className="empty-title">No products found</div>
            <div className="empty-sub">
              {search ? `No results for "${search}"` : 'Add your first product to get started'}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
