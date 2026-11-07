# Website: the Mono Shopify theme

A black-and-white Shopify theme for selling the plug-in ECUs: one heading face in bold capitals, hairline rules, the
board renders on white. [`preview/`](preview/) renders the same Liquid without a store.

| Folder | What's in it |
|---|---|
| `theme/` | The theme (Online Store 2.0). Zipped as `mono-theme.zip` |
| `products/` | `products.csv`: six draft products to import (one per model-year range and the daughterboard), with descriptions and spec tables. `make_products.py` rebuilds it |
| `product-images/` | The renders to upload as product photos |
| `preview/` | `render.js` (static preview with liquidjs) and `prep_images.py` (fits viewer renders into the theme's frames) |

## Setting up the store
1. **Theme:** Online Store → Themes → Add theme → Upload zip file → `mono-theme.zip`. Customise, then Publish.
2. **Products:** Products → Import → `products/products.csv`. Everything comes in as a **draft at $0.00**: set each
   price, upload its photo from `product-images/` (`ecu-8993.jpg` for 1989–93 and so on), then set it to Active. The
   1996–2005 products carry the tag `coming-soon`, which shows "Coming soon" instead of "Sold out"; set their inventory
   to 0 (or keep them drafts) until those boards are confirmed.
3. **Collection:** make one (e.g. "ECUs") with the products, and pick it in the homepage's *Shop* section.
4. **Menus** (Online Store → Navigation): `main-menu` with Shop `/#shop`, How it works `/#how`, Fit `/#fit`,
   FAQ `/#faq`; `footer` with Contact, Shipping, Returns, Privacy. For Contact, make a page with the `page.contact`
   template; it asks for the customer's car.
5. **Compatibility table:** in the theme editor each row can be linked to its product; the status text is yours to
   edit (Prototype / Coming later / In stock). Leave it empty to show In stock or Sold out from the product.
6. **Password page:** while you're still testing boards, keep the store's password on. The password page collects
   emails tagged `prelaunch`; the footer form tags sign-ups `newsletter`.

## Futura
Shopify removed Futura from its font library in 2025 (stores using it were switched to Jost), so the theme defaults to
**Jost**, Shopify's own replacement, which is very close. For real Futura, license it through Adobe Fonts (Futura PT
is in the Creative Cloud library): make a web project with Futura PT, then in Theme settings → Typography enter the
project ID and the family name (`futura-pt`). Headings switch to it; tick the box to use it for body text too.

## Before taking orders
- **The boards haven't been built or tested.** The theme's defaults say "Prototype" and point people at the email
  list. Keep checkout closed (store password, or products as drafts) until a prototype run passes on the bench and in
  a car.
- **Small print** (footer, editable): off-road and competition use only, and Mazda's trademarks with no affiliation.
  An engine computer that replaces the emissions-certified one isn't legal on a road car in the US; check what applies
  where you sell. Product names use "MX-5 Miata" to say what it fits; don't use Mazda's logos.
- **Firmware licence:** rusEFI is GPL. Selling boards with it flashed means offering the source (this repository and
  rusEFI's) to buyers.

## Rebuilding
```
npm i liquidjs @shopify/theme-check-node          # once, anywhere; point NODE_PATH at it
python3 products/make_products.py
NODE_PATH=…/node_modules node preview/render.js theme <out dir>   # preview pages
(cd theme && zip -qr ../mono-theme.zip .)          # the upload
```
Theme Check passes with two warnings, both the optional Adobe Fonts stylesheet (`RemoteAsset`).
