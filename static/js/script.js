document.addEventListener("DOMContentLoaded", function () {
    var menuIcon = document.querySelector(".menu-icon");
    var nav = document.querySelector("nav");

    if (menuIcon) {
        menuIcon.addEventListener("click", function () {
            console.log("Menu clicked"); // Debugging step
            nav.classList.toggle("active");
        });
    } else {
        console.error("Menu button not found!");
    }
});
