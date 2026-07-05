import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import ProductList from '../components/ProductList';
import { productApi } from '../services/api';
import { BrowserRouter } from 'react-router-dom';

// Mock the API service
jest.mock('../services/api', () => ({
  productApi: {
    getAll: jest.fn(),
    delete: jest.fn(),
  },
}));

// Mock useNavigate
const mockedUseNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockedUseNavigate,
}));

describe('ProductList', () => {
  const mockProducts = [
    { id: 1, name: 'Laptop Pro', description: 'Fast laptop', price: 1200, stock: 10, sku: 'LAP-001', status: 'ACTIVE', category: 'ELECTRONICS' },
    { id: 2, name: 'Office Chair', description: 'Comfortable chair', price: 250, stock: 5, sku: 'CHR-001', status: 'INACTIVE', category: 'FURNITURE' },
    { id: 3, name: 'Monitor 4K', description: 'High-res monitor', price: 500, stock: 20, sku: 'MON-001', status: 'ACTIVE', category: 'ELECTRONICS' },
  ];

  beforeEach(() => {
    productApi.getAll.mockClear();
    productApi.delete.mockClear();
    mockedUseNavigate.mockClear();
    productApi.getAll.mockResolvedValue({ data: mockProducts });
  });

  const renderComponent = () => {
    render(
      <BrowserRouter>
        <ProductList />
      </BrowserRouter>
    );
  };

  test('renders ProductList and checks total product count label for plural', async () => {
    renderComponent();

    expect(screen.getByText('Products')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Search by name or SKU…')).toBeInTheDocument();

    await waitFor(() => {
      expect(productApi.getAll).toHaveBeenCalledTimes(1);
      expect(productApi.getAll).toHaveBeenCalledWith(null);
      expect(screen.getByText('Laptop Pro')).toBeInTheDocument();
      // Total count label should say 'Showing 3 products'
      expect(screen.getByText('Showing 3 products')).toBeInTheDocument();
    });
  });

  test('updates product count label to singular when search narrows down to 1 product', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Showing 3 products')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search by name or SKU…');
    await userEvent.type(searchInput, 'Chair');

    await waitFor(() => {
      expect(screen.getByText('Showing 1 product')).toBeInTheDocument();
      expect(screen.getByText('Office Chair')).toBeInTheDocument();
      expect(screen.queryByText('Laptop Pro')).not.toBeInTheDocument();
    });
  });

  test('fetches products with category filter when category button is clicked', async () => {
    // For furniture button category filter
    productApi.getAll.mockResolvedValueOnce({ data: [mockProducts[1]] });

    renderComponent();

    await waitFor(() => expect(productApi.getAll).toHaveBeenCalledWith(null));
    productApi.getAll.mockClear();

    const furnitureBtn = screen.getByRole('button', { name: /FURNITURE/ });
    await userEvent.click(furnitureBtn);

    await waitFor(() => {
      expect(productApi.getAll).toHaveBeenCalledTimes(1);
      expect(productApi.getAll).toHaveBeenCalledWith('FURNITURE');
      expect(screen.getByText('Showing 1 product')).toBeInTheDocument();
    });
  });

  test('displays error message on API failure', async () => {
    productApi.getAll.mockRejectedValueOnce(new Error('API error'));

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('⚠️ Failed to load products. Is the backend running?')).toBeInTheDocument();
    });
  });

  test('handles product deletion', async () => {
    window.confirm = jest.fn(() => true);
    productApi.delete.mockResolvedValueOnce({});

    renderComponent();

    await waitFor(() => expect(screen.getByText('Laptop Pro')).toBeInTheDocument());

    const deleteButtons = screen.getAllByRole('button', { name: '🗑️' });
    await userEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(window.confirm).toHaveBeenCalledWith('Delete "Laptop Pro"? This cannot be undone.');
      expect(productApi.delete).toHaveBeenCalledWith(1);
      expect(screen.queryByText('Laptop Pro')).not.toBeInTheDocument();
      expect(screen.getByText('Showing 2 products')).toBeInTheDocument();
    });
  });
});
