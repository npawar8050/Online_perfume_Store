$(function() {
    // Function to fetch all products
    function fetchAllProducts() {
        // Make an AJAX call to fetch all products
        $.ajax({
            url: '/fetch_all_products',
            type: 'GET',
            success: function(allProducts) {
                displayProducts(allProducts);
            },
            error: function() {
                console.log('Error fetching products.');
            }
        });
    }

    // Display all products when the page loads
    fetchAllProducts();

    // Function to display products
    function displayProducts(products) {
        var productsDiv = $("#products");
        productsDiv.empty(); // Clear previous products

        // Display all products
        products.forEach(function(product) {
            var productHTML = `<div class="product">
                <h3>${product.name}</h3>
                <p>Price: $${product.price}</p>
                <!-- Other product details... -->
            </div>`;
            productsDiv.append(productHTML);
        });
    }
});
