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
 *       home:    function () { ... },
 *       // optional (L-310): when any of these four is passed, the
 *       // cluster draws a cross of arrows with Home at its centre.
 *       // A page with no 3D camera passes none and gets the three
 *       // buttons above, unchanged: one button, one meaning (L-285).
 *       stepLeft:  function () { ... },
 *       stepRight: function () { ... },
 *       stepUp:    function () { ... },
 *       stepDown:  function () { ... }
 *   });
 *
 * The cluster is position:absolute inside the container you pass, so
 * the container must be position:relative (or fixed/absolute) and is
 * expected to be the plot's own wrapper -- not the page body -- so the
 * buttons sit over the picture and never over a controls panel below
 * it. mount() returns { el, show(), hide(), crossApart(on) }.
 *
 * crossApart(true) moves the arrow cross -- Home with it -- into its own
 * holder, apart from + and -; crossApart(false) puts it back under them,
 * where mount() built it. It returns whether the cross is apart. WHERE the
 * holder sits is set only by the .nav-cross-apart rule below (the top-
 * right corner since 2026-09-16), so moving it again touches nothing
 * else. The page decides when: the exhibit rooms move it on a portrait
 * phone (L-316). A page with no step handlers has no cross, and
 * crossApart always returns false. The holder's class lets a page hide
 * it with its own rules (the exhibit rooms do while their drawer is
 * open).
 *
 * Buttons respond to click only. touch-action:manipulation removes the
 * 300 ms tap delay on phones, so no separate touchstart handler is
 * needed and none is wired; Plotly does not see these clicks because
 * the cluster is a sibling of the plot, not a child.
 *
 * Module written September 4, 2026 with Anthropic's Claude Fable 5.1.
 * Module updated September 10, 2026 with Anthropic's Claude Fable 5.1
 *   (L-310: optional arrow buttons in a cross around Home).
 * Module updated September 10, 2026 with Anthropic's Claude Opus 5
 *   (L-316: crossTop() moves the cross to the top centre on request).
 * Module updated September 10, 2026 with Anthropic's Claude Opus 5
 *   (L-316 round 2, Tony's Mode 5: the top centre covered the marker at
 *   the top of whichever shell fills the view, so the holder moves to the
 *   top-right corner; crossTop() is renamed crossRight()).
 * Module updated September 15, 2026 with Anthropic's Claude Opus 5
 *   (Tony's Mode 5: at the top right the cross covered the text of a
 *   hover box that opened over its marker, so the holder moves to the
 *   bottom-left corner above the drawer; crossRight() is renamed
 *   crossBottomLeft() and its class nav-cross-bottom-left).
 * Module updated September 16, 2026 with Anthropic's Claude Opus 5
 *   (Tony's Mode 5: the phone's text box now sits mid-view with no arrow,
 *   so the cross goes back to the top-right corner; the method is renamed
 *   once more, to crossApart(), and its class to nav-cross-apart, names
 *   that say nothing about the corner so the next move renames nothing).
 */
(function (global) {
    'use strict';

    var STYLE_ID = 'gallery-nav-cluster-style';

    var CSS = [
        '.nav-cluster {',
        '    position: absolute;',
        /* Top-left, Tony's ruling 2026-09-04 after the live page showed
           bottom-right under both the drawer and the info panel. The
           drawer owns the bottom, the panel owns the right (desktop) or
           the bottom (portrait), the title is centred: this corner is
           the one nothing else claims, on either room. On a portrait
           phone the rooms move the arrow cross out on its own -- to the
           top right on 2026-09-10 (L-316), to the bottom left above the
           drawer on 2026-09-15, and back to the top right on 2026-09-16
           (Tony's Mode 5) -- and + and - stay here. */
        '    left: 12px;',
        '    top: calc(12px + env(safe-area-inset-top, 0px));',
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
        '.nav-btn svg { display: block; }',
        /* L-310: the arrows and Home form a cross under + and -. */
        '.nav-cross {',
        '    display: grid;',
        '    grid-template-columns: repeat(3, 44px);',
        '    grid-template-rows: repeat(3, 44px);',
        '    gap: 6px;',
        '}',
        /* The cross's holder when the page moves it out on its own.
           THIS RULE IS THE ONLY PLACE ITS CORNER IS SET. Top right, 12 px
           in, as round 2 had it (2026-09-10); round 3 put it at the bottom
           left (2026-09-15) while the phone's text box still opened beside
           its marker; Tony moved it back on 2026-09-16 once that box sat
           mid-view. */
        '.nav-cross-apart {',
        '    position: absolute;',
        '    right: calc(12px + env(safe-area-inset-right, 0px));',
        '    top: calc(12px + env(safe-area-inset-top, 0px));',
        '    z-index: 6;',
        '}'
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

    /* L-310: one chevron, pointing up; rotated about the icon centre
       for the other three directions. */
    function svgChevron(deg) {
        return '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" ' +
            'stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">' +
            '<path d="M5 12.5 L10 7.5 L15 12.5" transform="rotate(' + deg + ' 10 10)"/></svg>';
    }

    function hasSteps(h) {
        return ['stepLeft', 'stepRight', 'stepUp', 'stepDown'].some(function (k) {
            return typeof h[k] === 'function';
        });
    }

    function place(btn, row, col) {
        btn.style.gridRow = String(row);
        btn.style.gridColumn = String(col);
        return btn;
    }

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
        var cross = null;
        if (hasSteps(handlers)) {
            cross = document.createElement('div');
            cross.className = 'nav-cross';
            cross.appendChild(place(button('Turn up',    svgChevron(0),   handlers.stepUp),    1, 2));
            cross.appendChild(place(button('Turn left',  svgChevron(270), handlers.stepLeft),  2, 1));
            cross.appendChild(place(button('Home',       SVG_HOME,        handlers.home),      2, 2));
            cross.appendChild(place(button('Turn right', svgChevron(90),  handlers.stepRight), 2, 3));
            cross.appendChild(place(button('Turn down',  svgChevron(180), handlers.stepDown),  3, 2));
            el.appendChild(cross);
        } else {
            el.appendChild(button('Home', SVG_HOME, handlers.home));
        }
        container.appendChild(el);

        /* L-316: the cross moves between the cluster and a holder of
           its own, whose corner the .nav-cross-apart rule sets. Moving the
           element keeps its buttons and handlers; putting it back appends
           it as the cluster's last child, which is where it was built, so
           the cluster's layout is unchanged. */
        var apartWrap = null;
        var isApart = false;
        var hidden = false;
        function crossApart(on) {
            on = !!on;
            if (!cross || on === isApart) { return isApart; }
            if (on) {
                if (!apartWrap) {
                    apartWrap = document.createElement('div');
                    apartWrap.className = 'nav-cross-apart';
                    apartWrap.setAttribute('role', 'group');
                    apartWrap.setAttribute('aria-label', 'Turn the view');
                    container.appendChild(apartWrap);
                }
                apartWrap.appendChild(cross);
                apartWrap.style.display = hidden ? 'none' : '';
            } else {
                el.appendChild(cross);
                apartWrap.style.display = 'none';
            }
            isApart = on;
            return isApart;
        }

        return {
            el: el,
            show: function () {
                hidden = false;
                el.style.display = '';
                if (apartWrap && isApart) { apartWrap.style.display = ''; }
            },
            hide: function () {
                hidden = true;
                el.style.display = 'none';
                if (apartWrap) { apartWrap.style.display = 'none'; }
            },
            crossApart: crossApart
        };
    }

    global.GalleryNav = { mount: mount };
})(window);
