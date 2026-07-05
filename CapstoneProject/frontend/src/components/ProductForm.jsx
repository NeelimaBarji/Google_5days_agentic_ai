import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { productApi } from '../services/api';

const EMPTY_FORM = {
  name: '', description: '', price: '', category: 'ELECTRONICS',
  stock: '', sku: '', status: 'ACTIVE',
};

export default function ProductForm() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const [form, setForm] = useState(EMPTY_FORM);
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (isEdit) {
      productApi.getById(id).then((res) => {
        const p = res.data;
        setForm({
          name: p.name, description: p.description || '',
          price: p.price, category: p.category,
          stock: p.stock, sku: p.sku, status: p.status,
        });
      });
    }
  }, [id, isEdit]);

  const validate = () => {
    const errs = {};
    if (!form.name.trim()) errs.name = 'Name is required';
    if (!form.price || form.price <= 0) errs.price = 'Price must be greater than 0';
    if (!form.sku.trim()) errs.sku = 'SKU is required';
    if (form.stock === '' || form.stock < 0) errs.stock = 'Stock must be ≥ 0';
    return errs;
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setErrors({ ...errors, [e.target.name]: null });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length > 0) { setErrors(errs); return; }
    setSaving(true);
    try {
      if (isEdit) {
        await productApi.update(id, form);
      } else {
        await productApi.create(form);
      }
      navigate('/');
    } catch (err) {
      alert(err.response?.data || 'Failed to save product');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="form-page">
      <div className="form-card">
        {/* Header */}
        <div className="form-card-header">
          <div className="header-icon">{isEdit ? '✏️' : '➕'}</div>
          <div>
            <h2>{isEdit ? 'Edit Product' : 'New Product'}</h2>
            <p>{isEdit ? 'Update product details below' : 'Fill in the details to add a product'}</p>
          </div>
        </div>

        {/* Body */}
        <div className="form-card-body">
          <form onSubmit={handleSubmit}>

            <div className="form-section-title">Basic Information</div>

            <div className="form-group">
              <label>Product Name <span className="req">*</span></label>
              <input
                name="name"
                value={form.name}
                onChange={handleChange}
                placeholder="e.g. Wireless Keyboard Pro"
              />
              {errors.name && <span className="field-error">⚠️ {errors.name}</span>}
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                name="description"
                value={form.description}
                onChange={handleChange}
                rows={3}
                placeholder="Optional product description…"
              />
            </div>

            <div className="form-section-title">Pricing & Inventory</div>

            <div className="form-row">
              <div className="form-group">
                <label>Price (USD) <span className="req">*</span></label>
                <input
                  name="price"
                  type="number"
                  step="0.01"
                  min="0"
                  value={form.price}
                  onChange={handleChange}
                  placeholder="0.00"
                />
                {errors.price && <span className="field-error">⚠️ {errors.price}</span>}
              </div>
              <div className="form-group">
                <label>Stock Quantity <span className="req">*</span></label>
                <input
                  name="stock"
                  type="number"
                  min="0"
                  value={form.stock}
                  onChange={handleChange}
                  placeholder="0"
                />
                {errors.stock && <span className="field-error">⚠️ {errors.stock}</span>}
              </div>
            </div>

            <div className="form-section-title">Classification</div>

            <div className="form-row">
              <div className="form-group">
                <label>SKU <span className="req">*</span></label>
                <input
                  name="sku"
                  value={form.sku}
                  onChange={handleChange}
                  disabled={isEdit}
                  placeholder="e.g. ELEC-001"
                />
                {errors.sku && <span className="field-error">⚠️ {errors.sku}</span>}
              </div>
              <div className="form-group">
                <label>Category</label>
                <select name="category" value={form.category} onChange={handleChange}>
                  <option value="ELECTRONICS">💻 Electronics</option>
                  <option value="FURNITURE">🪑 Furniture</option>
                  <option value="STATIONERY">✏️ Stationery</option>
                </select>
              </div>
              <div className="form-group">
                <label>Status</label>
                <select name="status" value={form.status} onChange={handleChange}>
                  <option value="ACTIVE">✅ Active</option>
                  <option value="INACTIVE">⏸ Inactive</option>
                  <option value="DISCONTINUED">🚫 Discontinued</option>
                </select>
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? '⏳ Saving…' : isEdit ? '✅ Update Product' : '➕ Create Product'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => navigate('/')}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
