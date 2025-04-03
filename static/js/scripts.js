document.querySelectorAll('.listen-now').forEach(link => {
    link.addEventListener('click', (e) => {
        if (!confirm('You will be redirected to YouTube. Continue?')) {
            e.preventDefault();
        }
    });
});