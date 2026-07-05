import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { productApi } from '../services/api';

const CAT_ICONS = { ELECTRONICS: '💻', FURNITURE: '🪑', STATIONERY: '✏️' };

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    productApi.getById(id)
      .then((res) => setProduct(res.data))
      .catch(() => navigate('/'))
      .finally(() => setLoading(false));
  }, [id, navigate]);

  const handleDelete = async () => {
    if (!window.confirm(`Delete "${product.name}"? This cannot be undone.`)) return;
    await productApi.delete(id);
    navigate('/');
  };

  if (loading) return (
    <div className="loading-wrap">
      <div className="spinner" />
      <span className="loading-text">Loading product…</span>
    </div>
  );
  if (!product) return null;

  return (
    <div className="detail-page">
      <div className="detail-card">
        {/* Hero */}
        <div className="detail-hero">
          <div className="detail-hero-top">
            <div>
              <div className="detail-sku-badge">{product.sku}</div>
              <h2>{product.name}</h2>
            </div>
            <div className="detail-hero-actions">
              <Link to={`/products/${id}/edit`} className="btn btn-hero-edit">✏️ Edit</Link>
              <button onClick={handleDelete} className="btn btn-hero-delete">🗑️ Delete</button>
              <Link to="/" className="btn btn-hero-back">← Back</Link>
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="detail-body">
          <div className="detail-grid">
            <div className="detail-field highlight">
              <label>Price</label>
              <span className="price-value">${parseFloat(product.price).toFixed(2)}</span>
            </div>

            <div className="detail-field">
              <label>Stock</label>
              <span className={product.stock < 10 ? 'stock-warning' : 'stock-ok'}>
                {product.stock < 10 ? `⚠️ ${product.stock} — Low Stock` : `${product.stock} units`}
              </span>
            </div>

            <div className="detail-field">
              <label>Category</label>
              <span>{CAT_ICONS[product.category]} {product.category}</span>
            </div>

            <div className="detail-field">
              <label>Status</label>
              <span className={`status-badge status-${product.status?.toLowerCase()}`}>
                {product.status}
              </span>
            </div>

            <div className="detail-field">
              <label>Created</label>
              <span>
                {product.createdAt
                  ? new Date(product.createdAt).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
                  : '—'}
              </span>
            </div>

            {product.description && (
              <div className="detail-field full-width">
                <label>Description</label>
                <span>{product.description}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
