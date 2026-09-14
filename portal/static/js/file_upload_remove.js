document.addEventListener("DOMContentLoaded", function () {

    // Remove newly selected file
    document.querySelectorAll("input[type='file']").forEach(function (input) {

        const container = input.parentElement;
        const removeButton = container.querySelector(".remove-selected-file");

        if (removeButton) {
            input.addEventListener("change", function () {
                removeButton.style.display =
                    input.files.length > 0 ? "inline-block" : "none";
            });

            removeButton.addEventListener("click", function () {
                input.value = "";
                removeButton.style.display = "none";
            });
        }
    });


    // Remove already saved/current file
    document.querySelectorAll(".remove-current-file").forEach(function (button) {

        button.addEventListener("click", function () {

            const checkboxId = button.previousElementSibling.id;
            const checkbox = document.getElementById(checkboxId);

            if (checkbox) {
                checkbox.checked = true;
            }

            button.parentElement.style.display = "none";
        });

    });

});