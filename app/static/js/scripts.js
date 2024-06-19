let lastScrollTop = 0;
const navbar = document.querySelector('.balk');

window.addEventListener('scroll', function() {
    let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    if (scrollTop > lastScrollTop) {
        navbar.style.top = '-60px'; 
    } else {
        navbar.style.top = '0';
    }
    lastScrollTop = scrollTop;
});
