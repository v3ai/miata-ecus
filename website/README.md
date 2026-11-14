# Website: the Mono Shopify theme

A black-and-white Shopify theme for selling the plug-in ECUs: one heading face in bold capitals, hairline rules, the
board renders on white. [`preview/`](preview/) renders the same Liquid without a store.

| Folder | What's in it |
|---|---|
| `theme/` | The theme (Online Store 2.0). Zipped as `mono-theme.zip` |
| `products/` | `products.csv`: five draft products to import, one per model-year range at $399, with descriptions and spec tables. `make_products.py` rebuilds it |
| `product-images/` | The renders to upload as product photos (`scripts/render_photos.py` redraws them and the theme's own copies from the current boards) |
| `preview/` | `render.js` (static preview with liquidjs) and `prep_images.py` (fits viewer renders into the theme's frames) |

## Setting up the store
1. **Theme:** Online Store → Themes → Add theme → Upload zip file → `mono-theme.zip`. Customise, then Publish.
2. **Products:** Products → Import → `products/products.csv`. All five come in as **drafts at $399**: upload each
   one's photo from `product-images/` (`ecu-8993.jpg` for 1989–93 and so on; 1989–93 and 1994–95 are the same board, so their two photos are the same render), then set it to Active when you're ready to
   sell. (The theme shows "Coming soon" instead of "Sold out" on any product tagged `coming-soon`.)
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
- **The boards haven't been built or tested.** The theme's defaults say "Prototype" for every year and point people
  at the email list. The 1996–2005 motherboards' outlines and mounting holes are still unmeasured placeholders. Keep checkout closed (store password, or products as drafts) until a prototype run passes on the bench and in
  a car.
- **"The most affordable Miata EFI":** the homepage backs it with "no other plug-in Miata ECU with a built-in
  wideband costs less", which held when checked on 2026-11-07 (MSPNP2 with internal wideband $1,199.99, VEMS plug-in
  $1,245, DIY-EFI CORE4 £465 ex VAT plus £70–120 for a wideband). Unassembled Speeduino kits without a wideband cost
  less, so keep the qualifier, and re-check before relying on the claim.
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
