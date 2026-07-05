package com.devloop.product.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "product")
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank(message = "Name is required")
    @Size(max = 200)
    private String name;

    @Size(max = 1000)
    private String description;

    @NotNull(message = "Price is required")
    @DecimalMin(value = "0.0", inclusive = false, message = "Price must be greater than 0")
    @Column(precision = 10, scale = 2)
    private BigDecimal price;

    @DecimalMin(value = "0.0", inclusive = true, message = "Discount must be between 0.0 and 1.0")
    @DecimalMax(value = "1.0", inclusive = true, message = "Discount must be between 0.0 and 1.0")
    @Column(precision = 3, scale = 2)
    private BigDecimal discount;

    @NotBlank(message = "Category is required")
    private String category;

    @Min(value = 0, message = "Stock cannot be negative")
    private Integer stock;

    @NotBlank(message = "SKU is required")
    @Column(unique = true)
    private String sku;

    @Enumerated(EnumType.STRING)
    private ProductStatus status = ProductStatus.ACTIVE;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();

    public enum ProductStatus {
        ACTIVE, INACTIVE, DISCONTINUED
    }

    public Product() {}

    // Getters
    public Long getId() { return id; }
    public String getName() { return name; }
    public String getDescription() { return description; }
    public BigDecimal getPrice() { return price; }
    public BigDecimal getDiscount() { return discount; }
    public String getCategory() { return category; }
    public Integer getStock() { return stock; }
    public String getSku() { return sku; }
    public ProductStatus getStatus() { return status; }
    public LocalDateTime getCreatedAt() { return createdAt; }

    // Setters
    public void setId(Long id) { this.id = id; }
    public void setName(String name) { this.name = name; }
    public void setDescription(String description) { this.description = description; }
    public void setPrice(BigDecimal price) { this.price = price; }
    public void setDiscount(BigDecimal discount) { this.discount = discount; }
    public void setCategory(String category) { this.category = category; }
    public void setStock(Integer stock) { this.stock = stock; }
    public void setSku(String sku) { this.sku = sku; }
    public void setStatus(ProductStatus status) { this.status = status; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    // Builder
    public static Builder builder() { return new Builder(); }

    public static class Builder {
        private Long id;
        private String name;
        private String description;
        private BigDecimal price;
        private BigDecimal discount;
        private String category;
        private Integer stock;
        private String sku;
        private ProductStatus status = ProductStatus.ACTIVE;
        private LocalDateTime createdAt = LocalDateTime.now();

        public Builder id(Long id) { this.id = id; return this; }
        public Builder name(String name) { this.name = name; return this; }
        public Builder description(String d) { this.description = d; return this; }
        public Builder price(BigDecimal p) { this.price = p; return this; }
        public Builder discount(BigDecimal d) { this.discount = d; return this; }
        public Builder category(String c) { this.category = c; return this; }
        public Builder stock(Integer s) { this.stock = s; return this; }
        public Builder sku(String sku) { this.sku = sku; return this; }
        public Builder status(ProductStatus s) { this.status = s; return this; }

        public Product build() {
            Product p = new Product();
            p.id = id; p.name = name; p.description = description;
            p.price = price; p.discount = discount; p.category = category; p.stock = stock;
            p.sku = sku; p.status = status; p.createdAt = createdAt;
            return p;
        }
    }
}
