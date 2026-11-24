/* Static preview of the Mono Shopify theme without a store: renders the theme's real Liquid with liquidjs, plus small
   stand-ins for Shopify's own tags, filters and objects, against made-up store data (products from
   ../products/products.json). Not what Shopify serves byte for byte, but the same templates, sections and CSS.
   usage: node render.js <theme dir> <out dir>      (needs liquidjs: npm i liquidjs)
   SITE=1: the static website instead (singularityboards.com on GitHub Pages, scripts in website/site/): a page per
   product, no cart, the products shown as coming soon (nothing is for sale until the prototypes pass), and the email
   sign-ups and the store's Contact / Shipping / Returns / Privacy pages replaced by links to the project on GitHub. */
'use strict';
const fs = require('fs');
const path = require('path');
const { Liquid, Tag, Value } = require('liquidjs');

const THEME = path.resolve(process.argv[2]);
const OUT = path.resolve(process.argv[3]);
const PRODUCTS = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'products', 'products.json'), 'utf8'));
const SITE = process.env.SITE === '1';
const STORE_NAME = process.env.STORE_NAME || (SITE ? 'Singularity Boards' : 'Store Name');
const REPO = 'https://github.com/v3ai/miata-ecus';
const read = (p) => fs.readFileSync(path.join(THEME, p), 'utf8');
const locale = JSON.parse(read('locales/en.default.json'));
const schemaOf = (src) => { const m = src.match(/\{%-?\s*schema\s*-?%\}([\s\S]*?)\{%-?\s*endschema\s*-?%\}/); return m ? JSON.parse(m[1]) : {}; };

const engine = new Liquid({ root: [path.join(THEME, 'snippets')], extname: '.liquid', jsTruthy: false, strictVariables: false, strictFilters: true });

/* ---------- tags ---------- */
function swallow(name, end) {
  engine.registerTag(name, class extends Tag {
    constructor(token, remain, liquid) { super(token, remain, liquid); while (remain.length) { const t = remain.shift(); if (t.name === end) return; } throw new Error(`no ${end}`); }
    * render() { return ''; }
  });
}
swallow('schema', 'endschema');
swallow('doc', 'enddoc');
swallow('javascript', 'endjavascript');
function wrapper(name, end, open, close, scope) {
  engine.registerTag(name, class extends Tag {
    constructor(token, remain, liquid) {
      super(token, remain, liquid);
      this.args = token.args; this.tpls = [];
      const stream = this.liquid.parser.parseStream(remain)
        .on(`tag:${end}`, () => stream.stop())
        .on('template', (tpl) => this.tpls.push(tpl))
        .on('end', () => { throw new Error(`${name} not closed`); });
      stream.start();
    }
    * render(ctx, emitter) {
      const extra = scope ? yield* scope(this, ctx) : {};
      emitter.write(typeof open === 'function' ? yield* open(this, ctx) : open);
      ctx.push(extra);
      yield this.liquid.renderer.renderTemplates(this.tpls, ctx, emitter);
      ctx.pop();
      emitter.write(close);
    }
  });
}
wrapper('style', 'endstyle', '<style>', '</style>');
const FORM_ACTIONS = { product: '/cart/add', customer: '/contact#footer', contact: '/contact', storefront_password: '/password' };
wrapper('form', 'endform', function* (tag, ctx) {
  const type = tag.args.match(/^\s*'([^']+)'/)[1];
  let attrs = '';
  for (const m of tag.args.matchAll(/([\w-]+):\s*('[^']*'|[\w.]+)/g)) {
    const v = m[2].startsWith("'") ? m[2].slice(1, -1) : yield new Value(m[2], tag.liquid).value(ctx, false);
    attrs += ` ${m[1]}="${v}"`;
  }
  return `<form method="post" action="${FORM_ACTIONS[type] || '#'}" accept-charset="UTF-8"${attrs}>`;
}, '</form>', function* () { return { form: { errors: null, 'posted_successfully?': false } }; });
wrapper('paginate', 'endpaginate', '', '', function* () { return { paginate: { pages: 1, parts: [], current_page: 1 } }; });

engine.registerTag('layout', class extends Tag { * render() { return ''; } });
engine.registerTag('section', class extends Tag {
  constructor(token, remain, liquid) { super(token, remain, liquid); this.name = token.args.match(/'([^']+)'/)[1]; }
  * render(ctx, emitter) { emitter.write(yield renderSection(this.name, {}, this.name, ctx.getAll())); }
});
engine.registerTag('sections', class extends Tag {
  constructor(token, remain, liquid) { super(token, remain, liquid); this.name = token.args.match(/'([^']+)'/)[1]; }
  * render(ctx, emitter) {
    const group = JSON.parse(read(`sections/${this.name}.json`));
    let html = '';
    for (const id of group.order) html += yield renderSection(group.sections[id].type, group.sections[id], id, ctx.getAll());
    emitter.write(html);
  }
});

/* ---------- filters ---------- */
const lookup = (key) => key.split('.').reduce((o, k) => (o == null ? o : o[k]), locale);
engine.registerFilter('t', function (key, ...args) {
  const opts = {}; for (const a of args) if (Array.isArray(a)) opts[a[0]] = a[1];
  let s = lookup(key);
  if (s && typeof s === 'object') s = opts.count === 1 ? s.one : s.other;
  if (s == null) return `[missing: ${key}]`;
  return String(s).replace(/\{\{\s*(\w+)\s*\}\}/g, (_, k) => (opts[k] ?? ''));
});
const kw = (args) => { const o = {}; for (const a of args) if (Array.isArray(a)) o[a[0]] = a[1]; return o; };
const money = (c) => (c == null ? '$—' : '$' + (c / 100).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ','));
engine.registerFilter('money', money);
engine.registerFilter('money_with_currency', (c) => (c == null ? '$—' : money(c) + ' USD'));
engine.registerFilter('money_without_currency', (c) => (c == null ? '' : (c / 100).toFixed(2)));
engine.registerFilter('asset_url', (n) => `assets/${n}`);
engine.registerFilter('shopify_asset_url', (n) => `#${n}`);
engine.registerFilter('stylesheet_tag', (u) => `<link rel="stylesheet" href="${u}">`);
engine.registerFilter('image_url', (img) => (img && img.src) || img || '');
engine.registerFilter('image_tag', (src, ...args) => {
  const o = kw(args);
  return `<img src="${src}" alt="${o.alt ?? ''}" width="2000" height="1300"${o.loading ? ` loading="${o.loading}"` : ''}${o.sizes ? ` sizes="${o.sizes}"` : ''}${o.class ? ` class="${o.class}"` : ''}>`;
});
engine.registerFilter('placeholder_svg_tag', (_, cls) => `<svg class="${cls || ''}" viewBox="0 0 525 525" xmlns="http://www.w3.org/2000/svg"><rect x="160" y="160" width="205" height="205"/></svg>`);
engine.registerFilter('font_face', () => '');
engine.registerFilter('font_modify', (f) => f);
engine.registerFilter('handle', (s) => String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''));
engine.registerFilter('default_errors', () => '');
engine.registerFilter('payment_button', () => '');
engine.registerFilter('media_tag', () => '');
engine.registerFilter('time_tag', (d) => String(d));
engine.registerFilter('format_address', () => '');
engine.registerFilter('format_code', (s) => s);
engine.registerFilter('link_to', (t, u) => `<a href="${u}">${t}</a>`);

/* ---------- store data ---------- */
const settingsSchema = JSON.parse(read('config/settings_schema.json'));
const settings = { ...JSON.parse(read('config/settings_data.json')).current };
for (const g of settingsSchema) for (const s of g.settings || []) if (s.id && settings[s.id] === undefined && s.default !== undefined) settings[s.id] = s.default;
settings.type_heading_font = { family: 'Jost', fallback_families: 'sans-serif', weight: 700 };
settings.type_body_font = { family: 'Jost', fallback_families: 'sans-serif', weight: 400 };

const PAGES = { home: 'index.html', product: 'product.html', cart: SITE ? 'index.html#shop' : 'cart.html', collection: 'collection.html' };
// Variants from products.json (Package: Board only / Complete kit); a product without them gets one default variant
function variantsOf(p, i) {
  const vs = (p.variants && p.variants.length ? p.variants : [{ title: 'Default Title', price: '399.00' }])
    .map((v, k) => ({ id: 1000 + 10 * i + k, title: v.title, price: Math.round(parseFloat(v.price) * 100), available: true, options: [v.title] }));
  const only = vs.length === 1 && vs[0].title === 'Default Title';
  const prices = vs.map((v) => v.price);
  return {
    price: Math.min(...prices), compare_at_price: null, price_varies: new Set(prices).size > 1, available: true,
    has_only_default_variant: only,
    options_with_values: only ? [] : [{ name: 'Package', position: 1, values: vs.map((v) => v.title), selected_value: vs[0].title }],
    variants: vs,
  };
}
const products = PRODUCTS.map((p, i) => {
  const img = { src: `assets/${p.image}-1200.jpg`, alt: p.title, media_type: 'image' };
  return {
    id: i + 1, title: p.title, handle: p.handle, url: SITE ? `products/${p.handle}.html` : PAGES.product, type: p.type, description: p.body,
    tags: p.tags.split(', ').concat(SITE ? ['coming-soon'] : []),
    featured_media: img, media: [img, { src: 'assets/render-assembly-lifted-1200.jpg', alt: 'Exploded', media_type: 'image' }],
    ...variantsOf(p, i),
  };
});
// the website sells nothing yet: every product and variant unavailable, so the theme shows "Coming soon"
if (SITE) for (const p of products) { p.available = false; for (const v of p.variants) v.available = false; }
products.forEach((p) => { p.selected_or_first_available_variant = p.variants[0]; });
const collection = { title: 'Shop', url: PAGES.collection, products, products_count: products.length, description: '' };
const menus = {
  'main-menu': { links: [['Shop', `${PAGES.home}#shop`], ['How it works', `${PAGES.home}#how`], ['Fit', `${PAGES.home}#fit`], ['FAQ', `${PAGES.home}#faq`]] },
  footer: { links: SITE
    ? [['Source on GitHub', REPO], ['Install guide', `${REPO}/blob/main/INSTALL.md`], ['Build guide', `${REPO}/blob/main/BUILD.md`], ['3D viewer', 'viewer/']]
    : [['Contact', '#'], ['Shipping', '#'], ['Returns', '#'], ['Privacy', '#']] },
};
// website: the texts that point at the store's email sign-up point at the project instead
const SITE_TEXT = {
  announcement: 'Prototype run: not for sale yet',
  cta: { eyebrow: 'Prototype', heading: 'Follow the build.', button_label: 'On GitHub', button_link: REPO,
         text: '<p>The first boards are being built and tested; nothing is for sale yet. The designs, firmware and build notes are all open.</p>' },
  ship: '<p>The first boards are being built and tested. Nothing is for sale until they pass on the bench and in a car: follow the project on GitHub for news.</p>',
};
const linkList = (h) => ({ links: (menus[h] || { links: [] }).links.map(([title, url]) => ({ title, url, active: false })) });

function resolveSettings(schemaSettings, given) {
  const out = {};
  for (const s of schemaSettings || []) {
    if (!s.id) continue;
    let v = given && given[s.id] !== undefined ? given[s.id] : s.default;
    if (s.type === 'link_list') v = linkList(v);
    if (s.type === 'collection') v = v ? collection : null;
    if (s.type === 'product') v = v ? products[0] : null;
    if (s.type === 'image_picker') v = v || null;
    if (v === undefined) v = null;
    out[s.id] = v;
  }
  return out;
}

async function renderSection(type, data, id, scope) {
  const src = read(`sections/${type}.liquid`);
  if (SITE) {
    data = JSON.parse(JSON.stringify(data || {}));
    data.settings = data.settings || {};
    if (type === 'footer') data.settings.show_newsletter = false;
    if (data.settings.announcement) data.settings.announcement = SITE_TEXT.announcement;
    if (id === 'cta') Object.assign(data.settings, SITE_TEXT.cta);
    for (const b of Object.values(data.blocks || {}))
      if (b.settings && /sign up below/i.test(b.settings.answer || '')) b.settings.answer = SITE_TEXT.ship;
  }
  const schema = schemaOf(src);
  const settingsIn = { ...(data.settings || {}) };
  if (type === 'featured-collection' && !settingsIn.collection) settingsIn.collection = 'preview';
  const blocks = (data.block_order || []).map((bid) => {
    const b = data.blocks[bid];
    const bs = (schema.blocks || []).find((x) => x.type === b.type) || {};
    return { id: bid, type: b.type, settings: resolveSettings(bs.settings, b.settings), shopify_attributes: '' };
  });
  const section = { id, settings: resolveSettings(schema.settings, settingsIn), blocks };
  const globals = { ...scope }; delete globals.section;
  const html = await engine.parseAndRender(src, { ...scope, section }, { globals });
  const tag = schema.tag || 'div';
  return `<${tag} id="shopify-section-${id}" class="shopify-section ${schema.class || ''}">${html}</${tag}>`;
}

async function page(file, template, scopeExtra, overrides) {
  const scope = {
    shop: { name: STORE_NAME, money_format: '${{amount}}', customer_accounts_enabled: false, description: '' },
    settings, cart: { item_count: 1, items: [], total_price: null, currency: { iso_code: 'USD' } },
    routes: { root_url: PAGES.home, cart_url: PAGES.cart, search_url: '#', account_url: '#', all_products_collection_url: PAGES.collection },
    request: { locale: { iso_code: 'en' }, page_type: template, origin: '' }, template: { name: template },
    canonical_url: '', page_title: STORE_NAME, content_for_header: '', powered_by_link: SITE ? '' : '<a href="https://www.shopify.com">Powered by Shopify</a>',
    current_page: 1, ...scopeExtra,
  };
  const tpl = JSON.parse(read(`templates/${template}.json`));
  let body = '';
  for (const id of tpl.order) {
    const data = JSON.parse(JSON.stringify(tpl.sections[id]));
    if (overrides && overrides[id]) Object.assign(data.settings, overrides[id]);
    body += await renderSection(data.type, data, id, scope);
  }
  let html = await engine.parseAndRender(read(`layout/${tpl.layout || 'theme'}.liquid`), { ...scope, content_for_layout: body }, { globals: scope });
  // the preview loads Jost from Google Fonts in place of Shopify's font CDN
  html = html.replace('</head>', '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:ital,wght@0,400;0,700;1,400&display=swap"></head>');
  if (SITE) {
    html = html.replace(/<a href="[^"]*" id="cart-link">[\s\S]*?<\/a>/, '');               // no cart
    html = html.replace(/\s*<link rel="preconnect" href="https:\/\/fonts\.shopifycdn\.com"[^>]*>/, '');
    // pages in products/ reach the rest with ../; the 404 page is served at any depth, so it uses root links
    const pre = file === '404.html' ? '/' : '../'.repeat(file.split('/').length - 1);
    if (pre) html = html.replace(/(href|src)="(?![a-z]+:|\/|#)([^"]*)"/g, (m, a, u) => `${a}="${pre}${u}"`);
  }
  fs.mkdirSync(path.dirname(path.join(OUT, file)), { recursive: true });
  fs.writeFileSync(path.join(OUT, file), html);
  console.log('wrote', file, html.length);
}

(async () => {
  fs.mkdirSync(path.join(OUT, 'assets'), { recursive: true });
  for (const f of fs.readdirSync(path.join(THEME, 'assets'))) fs.copyFileSync(path.join(THEME, 'assets', f), path.join(OUT, 'assets', f));
  await page(PAGES.home, 'index', {});
  if (SITE) {
    for (const p of products) await page(p.url, 'product', { product: p, page_title: p.title });
    await page(PAGES.collection, 'collection', { collection, page_title: 'Shop' });
    await page('404.html', '404', { page_title: 'Not found' });
    return;
  }
  const product = products[0];
  await page(PAGES.product, 'product', { product, page_title: product.title });
  await page(PAGES.collection, 'collection', { collection, page_title: 'Shop' });
  const item = { url: PAGES.product, image: product.featured_media, product, variant: product.variants[0], properties: [], final_price: product.variants[0].price,
    final_line_price: product.variants[0].price, quantity: 1, key: 'k1', url_to_remove: '#', line_level_discount_allocations: [] };
  await page(PAGES.cart, 'cart', { cart: { item_count: 1, items: [item], total_price: product.variants[0].price, cart_level_discount_applications: [], currency: { iso_code: 'USD' } }, page_title: 'Cart' });
})().catch((e) => { console.error(e); process.exit(1); });
