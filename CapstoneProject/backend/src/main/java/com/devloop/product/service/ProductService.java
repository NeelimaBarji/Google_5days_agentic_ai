package com.devloop.product.service;

import com.devloop.product.entity.Product;
import com.devloop.product.repository.ProductRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional
public class ProductService {

    private static final Logger log = LoggerFactory.getLogger(ProductService.class);

    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public List<Product> findAll() {
        log.debug("Fetching all products");
        return productRepository.findAll();
    }

    public List<Product> findByCategory(String category) {
        log.debug("Fetching products by category: {}", category);
        return productRepository.findByCategory(category);
    }

    public Product findById(Long id) {
        return productRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Product not found with id: " + id));
    }

    public Product create(Product product) {
        if (productRepository.existsBySku(product.getSku())) {
            throw new RuntimeException("Product with SKU already exists: " + product.getSku());
        }
        log.debug("Creating product: {}", product.getName());
        return productRepository.save(product);
    }

    public Product update(Long id, Product updatedProduct) {
        Product existing = findById(id);
        existing.setName(updatedProduct.getName());
        existing.setDescription(updatedProduct.getDescription());
        existing.setPrice(updatedProduct.getPrice());
        existing.setCategory(updatedProduct.getCategory());
        existing.setStock(updatedProduct.getStock());
        existing.setStatus(updatedProduct.getStatus());
        existing.setDiscount(updatedProduct.getDiscount()); // Added discount update
        log.debug("Updating product id: {}", id);
        return productRepository.save(existing);
    }

    public void delete(Long id) {
        findById(id);
        log.debug("Deleting product id: {}", id);
        productRepository.deleteById(id);
    }

    public List<Product> findLowStock(Integer threshold) {
        return productRepository.findByStockLessThan(threshold);
    }
}
