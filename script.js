document.getElementById("emailForm").addEventListener("submit", function(event) {
    event.preventDefault();

    let name = document.getElementById("name").value;
    let email = document.getElementById("email").value;
    let message = document.getElementById("message").value;
    let responseMessage = document.getElementById("responseMessage");

    if (name && email && message) {
        // Simulating email submission (Replace with backend logic)
        responseMessage.textContent = "Thank you for reaching out! I'll get back to you soon.";
        responseMessage.style.color = "lightgreen";
        
        // Clear form fields
        document.getElementById("emailForm").reset();
    } else {
        responseMessage.textContent = "Please fill out all fields.";
        responseMessage.style.color = "red";
    }
});
