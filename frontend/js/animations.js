export function observeCards() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px 0px 0px" // Reduzido o rootMargin negativo para aparecer mais rápido
    };

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                obs.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        // Removemos o transitionDelay que causava atraso nas estilizações de hover e scroll
        card.style.transitionDelay = '0s'; 
        observer.observe(card);
    });
}
