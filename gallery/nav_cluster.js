/* nav_cluster.js -- the gallery's three-button navigation cluster.
 *
 * One control set for the whole site, Tony's ruling 2026-09-03: the
 * same three buttons, in the same corner, on every page and every
 * screen size. What the buttons DO is the page's business; this file
 * only draws them and calls back.
 *
 *   +     zoom in
 *   -     zoom out
 *   Home  back to the arrival view
 *
 * The look is copied from index.html's .zoom-btn cluster (44 px, 10 px
 * radius, translucent dark, blurred) so the interactive wing matches
 * the static gallery the visitor has just come from. The static
 * gallery keeps its own inline cluster until index.html next opens;
 * when it adopts this file the two copies become one.
 *
 * Home is a house glyph, deliberately not a circular arrow: on a phone
 * the browser's own reload button sits an inch below this cluster and
 * throws the whole page away.
 *
 * Usage (one call, after the DOM exists):
 *
 *   GalleryNav.mount(document.querySelector('.viz-area'), {
 *       zoomIn:  function () { ... },
 *       zoomOut: function () { ... },
 *       home:    function () { ... }
 *   });
 *
 * The cluster is position:absolute inside the container you pass, so
 * the container must be position:relative (or fixed/absolute) and is
 * expected to be the plot's own wrapper -- not the page body -- so the
 * buttons sit over the picture and never over a controls panel below
 * it. mount() returns { el, show(), hide() }.
 *
 * Buttons respond to click only. touch-action:manipulation removes the
 * 300 ms tap delay on phones, so no separate touchstart handler is
 * needed and none is wired; Plotly does not see these clicks because
 * the cluster is a sibling of the plot, not a child.
 *
 * Module written September 4, 2026 with Anthropic's Claude Fable 5.1.
 */
(function (global) {
    'use strict';

    var STYLE_ID = 'gallery-nav-cluster-style';

    var CSS = [
        '.nav-cluster {',
        '    position: absolute;',
        '    right: 12px;',
        /* Above the Sun room drawer handle, which sits centred in a
           64 px bottom band; on the Explorer the band is empty and the
           gap is harmless. */
        '    bottom: calc(64px + env(safe-area-inset-bottom, 0px));',
        '    z-index: 6;',
        '    display: flex;',
        '    flex-direction: column;',
        '    gap: 6px;',
        '}',
        '.nav-btn {',
        '    width: 44px;',
        '    height: 44px;',
        '    border-radius: 10px;',
        '    border: 1px solid var(--border, rgba(255,255,255,0.12));',
        '    background: rgba(18, 18, 26, 0.85);',
        '    backdrop-filter: blur(8px);',
        '    -webkit-backdrop-filter: blur(8px);',
        '    color: var(--text-secondary, #b8b6b3);',
        '    cursor: pointer;',
        '    display: flex;',
        '    align-items: center;',
        '    justify-content: center;',
        '    padding: 0;',
        '    transition: all 0.15s;',
        '    -webkit-tap-highlight-color: transparent;',
        '    touch-action: manipulation;',
        '    -webkit-user-select: none;',
        '    user-select: none;',
        '    -webkit-touch-callout: none;',
        '}',
        '.nav-btn:hover {',
        '    border-color: var(--accent, #c9a961);',
        '    color: var(--accent, #c9a961);',
        '}',
        '.nav-btn:active {',
        '    background: rgba(18, 18, 26, 0.95);',
        '    transform: scale(0.93);',
        '}',
        '.nav-btn svg { display: block; }'
    ].join('\n');

    var SVG_PLUS =
        '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" ' +
        'stroke="currentColor" stroke-width="2.5" stroke-linecap="round">' +
        '<line x1="10" y1="4" x2="10" y2="16"/><line x1="4" y1="10" x2="16" y2="10"/></svg>';

    var SVG_MINUS =
        '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" ' +
        'stroke="currentColor" stroke-width="2.5" stroke-linecap="round">' +
        '<line x1="4" y1="10" x2="16" y2="10"/></svg>';

    /* A house: roof, walls, door. Outline only, same stroke as + and -. */
    var SVG_HOME =
        '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" ' +
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
        '<path d="M3 10 L10 3.5 L17 10"/>' +
        '<path d="M5 9 V16.5 H15 V9"/>' +
        '<path d="M8.5 16.5 V12 H11.5 V16.5"/></svg>';

    function injectStyle() {
        if (document.getElementById(STYLE_ID)) { return; }
        var s = document.createElement('style');
        s.id = STYLE_ID;
        s.textContent = CSS;
        document.head.appendChild(s);
    }

    function button(label, svg, onClick) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'nav-btn';
        b.setAttribute('aria-label', label);
        b.title = label;
        b.innerHTML = svg;
        b.addEventListener('click', function (e) {
            e.preventDefault();
            if (typeof onClick === 'function') { onClick(); }
        });
        return b;
    }

    function mount(container, handlers) {
        if (!container) { return null; }
        handlers = handlers || {};
        injectStyle();
        var el = document.createElement('div');
        el.className = 'nav-cluster';
        el.setAttribute('role', 'group');
        el.setAttribute('aria-label', 'Navigation');
        el.appendChild(button('Zoom in', SVG_PLUS, handlers.zoomIn));
        el.appendChild(button('Zoom out', SVG_MINUS, handlers.zoomOut));
        el.appendChild(button('Home', SVG_HOME, handlers.home));
        container.appendChild(el);
        return {
            el: el,
            show: function () { el.style.display = ''; },
            hide: function () { el.style.display = 'none'; }
        };
    }

    global.GalleryNav = { mount: mount };
})(window);
