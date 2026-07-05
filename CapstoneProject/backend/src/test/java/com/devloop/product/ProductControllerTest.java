package com.devloop.product;

import com.devloop.product.entity.Product;
import com.devloop.product.service.ProductService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(controllers = com.devloop.product.controller.ProductController.class)
class ProductControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ProductService productService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void findAll_returnsProductList() throws Exception {
        Product p = Product.builder()
                .id(1L).name("Mouse").price(BigDecimal.valueOf(29.99))
                .category("ELECTRONICS").stock(100).sku("ELEC-001")
                .discount(BigDecimal.valueOf(0.15))
                .build();
        when(productService.findAll()).thenReturn(List.of(p));

        mockMvc.perform(get("/api/products"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].name").value("Mouse"))
                .andExpect(jsonPath("$[0].category").value("ELECTRONICS"))
                .andExpect(jsonPath("$[0].discount").value(0.15));
    }

    @Test
    void findById_returnsProductWithDiscount() throws Exception {
        Product p = Product.builder()
                .id(1L).name("Mouse").price(BigDecimal.valueOf(29.99))
                .category("ELECTRONICS").stock(100).sku("ELEC-001")
                .discount(BigDecimal.valueOf(0.15))
                .build();
        when(productService.findById(1L)).thenReturn(p);

        mockMvc.perform(get("/api/products/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Mouse"))
                .andExpect(jsonPath("$.discount").value(0.15));
    }

    @Test
    void create_validProduct_returnsCreated() throws Exception {
        Product p = Product.builder()
                .name("Keyboard").price(BigDecimal.valueOf(89.99))
                .category("ELECTRONICS").stock(50).sku("ELEC-010")
                .discount(BigDecimal.valueOf(0.10))
                .build();
        when(productService.create(any())).thenReturn(p);

        mockMvc.perform(post("/api/products")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(p)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.name").value("Keyboard"))
                .andExpect(jsonPath("$.discount").value(0.10));
    }

    @Test
    void create_productWithInvalidDiscount_returnsBadRequest() throws Exception {
        Product p = Product.builder()
                .name("Invalid Discount Product").price(BigDecimal.valueOf(10.00))
                .category("TEST").stock(10).sku("TEST-001")
                .discount(BigDecimal.valueOf(1.10)) // Invalid discount
                .build();

        // Mocking the service to throw an exception if validation fails in service or controller
        // For @Valid, the controller handles it before service, so we expect a 400 status directly
        mockMvc.perform(post("/api/products")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(p)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void update_validProductWithDiscount_returnsOk() throws Exception {
        Long productId = 1L;
        Product existing = Product.builder()
                .id(productId).name("Mouse").price(BigDecimal.valueOf(29.99))
                .category("ELECTRONICS").stock(100).sku("ELEC-001")
                .discount(BigDecimal.valueOf(0.0))
                .build();

        Product updated = Product.builder()
                .id(productId).name("Updated Mouse").price(BigDecimal.valueOf(25.99))
                .category("ELECTRONICS").stock(90).sku("ELEC-001")
                .discount(BigDecimal.valueOf(0.20))
                .build();

        when(productService.update(eq(productId), any(Product.class))).thenReturn(updated);

        mockMvc.perform(put("/api/products/{id}", productId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updated)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Updated Mouse"))
                .andExpect(jsonPath("$.discount").value(0.20));
    }

    @Test
    void update_productWithInvalidDiscount_returnsBadRequest() throws Exception {
        Long productId = 1L;
        Product updated = Product.builder()
                .id(productId).name("Mouse").price(BigDecimal.valueOf(29.99))
                .category("ELECTRONICS").stock(100).sku("ELEC-001")
                .discount(BigDecimal.valueOf(-0.05)) // Invalid discount
                .build();

        // Expecting bad request due to @Valid annotations on the Product DTO in the controller
        mockMvc.perform(put("/api/products/{id}", productId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updated)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void findById_notFound_returnsBadRequest() throws Exception {
        when(productService.findById(99L)).thenThrow(new RuntimeException("Product not found with id: 99"));

        mockMvc.perform(get("/api/products/99"))
                .andExpect(status().isBadRequest());
    }

    @Test
    void lowStock_returnsFilteredProducts() throws Exception {
        Product p = Product.builder()
                .id(2L).name("USB Hub").price(BigDecimal.valueOf(39.99))
                .category("ELECTRONICS").stock(3).sku("ELEC-003")
                .discount(BigDecimal.valueOf(0.0))
                .build();
        when(productService.findLowStock(10)).thenReturn(List.of(p));

        mockMvc.perform(get("/api/products/low-stock?threshold=10"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].stock").value(3));
    }
}
