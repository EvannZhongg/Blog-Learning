// declaraction of document.ready() function.
(function () {
    var ie = !!(window.attachEvent && !window.opera);
    var wk = /webkit\/(\d+)/i.test(navigator.userAgent) && (RegExp.$1 < 525);
    var fn = [];
    var run = function () {
        for (var i = 0; i < fn.length; i++) fn[i]();
    };
    var d = document;
    d.ready = function (f) {
        if (!ie && !wk && d.addEventListener)
            return d.addEventListener('DOMContentLoaded', f, false);
        if (fn.push(f) > 1) return;
        if (ie)
            (function () {
                try {
                    d.documentElement.doScroll('left');
                    run();
                } catch (err) {
                    setTimeout(arguments.callee, 0);
                }
            })();
        else if (wk)
            var t = setInterval(function () {
                if (/^(loaded|complete)$/.test(d.readyState))
                    clearInterval(t), run();
            }, 0);
    };
})();

document.ready(
    () => {
        var _Blog = window._Blog || {};
        const currentTheme = window.localStorage && window.localStorage.getItem('theme');
        const isDark = currentTheme === 'dark';
        const pagebody = document.getElementsByTagName('body')[0];

        // 获取代码高亮样式 link 元素
        const hljsTheme = document.getElementById('hljs-theme');

        function updateCodeHighlightStyle(isDarkMode) {
            if (!hljsTheme) return;
            const newHref = isDarkMode
                ? "https://cdn.jsdelivr.net/npm/highlight.js@11.7.0/styles/github-dark.css"
                : "https://cdn.jsdelivr.net/npm/highlight.js@11.7.0/styles/github.css";
            hljsTheme.setAttribute('href', newHref);
        }


        // 初始化切换按钮状态
        if (isDark) {
            document.getElementById("switch_default").checked = true;
            document.getElementById("mobile-toggle-theme").innerText = "· Dark";
            pagebody.classList.add('dark-theme');
        } else {
            document.getElementById("switch_default").checked = false;
            document.getElementById("mobile-toggle-theme").innerText = "· Light";
            pagebody.classList.remove('dark-theme');
        }

        // 初始同步代码高亮样式
        updateCodeHighlightStyle(isDark);

        _Blog.toggleTheme = function () {
            const toggleBtn = document.getElementsByClassName('toggleBtn')[0];
            const mobileBtn = document.getElementById('mobile-toggle-theme');

            // 桌面端切换按钮
            toggleBtn.addEventListener('click', () => {
                const isNowDark = !pagebody.classList.contains('dark-theme');
                if (isNowDark) {
                    pagebody.classList.add('dark-theme');
                    mobileBtn.innerText = "· Dark";
                } else {
                    pagebody.classList.remove('dark-theme');
                    mobileBtn.innerText = "· Light";
                }
                window.localStorage &&
                window.localStorage.setItem('theme', isNowDark ? 'dark' : 'light');

                updateCodeHighlightStyle(isNowDark);
            });

            // 移动端切换按钮
            mobileBtn.addEventListener('click', () => {
                const isNowDark = !pagebody.classList.contains('dark-theme');
                if (isNowDark) {
                    pagebody.classList.add('dark-theme');
                    mobileBtn.innerText = "· Dark";
                } else {
                    pagebody.classList.remove('dark-theme');
                    mobileBtn.innerText = "· Light";
                }
                window.localStorage &&
                window.localStorage.setItem('theme', isNowDark ? 'dark' : 'light');

                updateCodeHighlightStyle(isNowDark);
            });
        };

        _Blog.toggleTheme();
    }
);
