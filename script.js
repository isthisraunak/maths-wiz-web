document.getElementById("emailForm").addEventListener("submit", function(event) {
    let responseMessage = document.getElementById("responseMessage");
    
    responseMessage.textContent = "Sending...";
    responseMessage.style.color = "#00e676";
    
    setTimeout(() => {
        responseMessage.textContent = "Thank you! Your message has been sent.";
    }, 2000);
});
