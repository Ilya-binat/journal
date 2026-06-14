document.addEventListener("DOMContentLoaded", () => {
    const wrapper = document.getElementById("weekDaysWrapper");
    const params = new URLSearchParams(window.location.search);
    // АНИМАЦИЯ НЕДЕЛИ
    if (params.get("nav") === "week") {
        wrapper.classList.add("slide-in");
        requestAnimationFrame(() => {
            wrapper.classList.remove("slide-in");
        });
    }

    // СТРЕЛКИ
    document.querySelectorAll(".week-nav").forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            const url = this.href;
            wrapper.style.pointerEvents = "none";
            wrapper.classList.add(
                this.classList.contains("next")
                    ? "slide-next"
                    : "slide-prev"
            );
            setTimeout(() => {
                window.location.href = url;
            }, 520);
        });
    });
    // ДНИ
    document.querySelectorAll(".week-day").forEach(day => {
        day.addEventListener("click", function (e) {
            e.preventDefault();
            window.location.href = this.href;
        });
    });
    // COMMENTS
    document.querySelectorAll(".comment-toggle-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            const card = this.closest(".card-body");
            const box = card.querySelector(".comment-box");
            box.classList.toggle("open");
        });
    });
    //    EDIT COMMENT
    document.querySelectorAll(".btn-edit").forEach(btn => {
        btn.addEventListener("click", function () {
            const box = document.getElementById(
                this.dataset.target
            );

            box.classList.toggle("open");
        });
    });
});
