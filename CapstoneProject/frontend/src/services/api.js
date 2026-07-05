import axios from 'axios';

const BASE_URL = '/api/products';

export const productApi = {
  getAll: (category) => {
    const params = category ? { category } : {};
    return axios.get(BASE_URL, { params });
  },

  getById: (id) => axios.get(`${BASE_URL}/${id}`),

  create: (product) => axios.post(BASE_URL, product),

  update: (id, product) => axios.put(`${BASE_URL}/${id}`, product),

  delete: (id) => axios.delete(`${BASE_URL}/${id}`),

  getLowStock: (threshold = 10) =>
    axios.get(`${BASE_URL}/low-stock`, { params: { threshold } }),
};
