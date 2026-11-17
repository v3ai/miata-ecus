"""Writes products.csv (Shopify product import: one ECU per model-year range, each as board only at $350 or a complete kit
at $500, as drafts until the boards are proven)
and products.json (the same data, for the theme preview). usage: python3 make_products.py"""
import csv, json, os
here = os.path.dirname(os.path.abspath(__file__))

COMMON = [
    ('Processor', 'STM32F407, running rusEFI'),
    ('Wideband', 'Built-in LSU 4.9 controller'),
    ('MAP sensor', '700 kPa absolute, on the board'),
    ('Outputs', '8 low-side drivers, 7 protected relay and lamp outputs, 4 ignition'),
    ('Tuning', 'TunerStudio over USB-C'),
]
VARIANTS = [('Board only', '350.00', ''), ('Complete kit', '500.00', '-kit')]   # (Package option, price, SKU suffix)
INCLUDED = ('A GM air temperature sensor with its plug, terminals and 2 m of wire, for the car\'s own air '
            'temperature wires (the firmware is set for it)')
YOU_ADD = 'A Bosch LSU 4.9 sensor (it fits the stock front oxygen sensor\'s hole) and its lead, a vacuum hose to the intake manifold, your stock ECU case'
KIT_ADDS = ('A Bosch LSU 4.9 sensor with a lead made up for this board, 3 m of 4 mm silicone vacuum hose and a tee, '
            'a 3 m USB cable and case washers. You add your stock ECU case')

YEARS = [
    dict(key='8993', years='1989–93', title='Plug-in ECU 1989–93', chassis='NA · 1.6', connector='Stock 48-pin (2 plugs)',
         fits='1989–93 MX-5 Miata, manual and manual-swapped', status='Prototype',
         extra='<p>The 1989–93 manual cars have a throttle switch rather than a throttle position sensor. For closed-loop idle '
               'and throttle-based acceleration fuel, add a 0–5 V sensor on the stock plug: two 0 Ω links on the board.</p>'),
    dict(key='9495', years='1994–95', title='Plug-in ECU 1994–95', chassis='NA · 1.8', connector='Stock 48-pin (2 plugs)',
         fits='1994–95 MX-5 Miata, manual and manual-swapped', status='Prototype', extra=''),
    dict(key='9697', years='1996–97', title='Plug-in ECU 1996–97', chassis='NA · 1.8 OBD-II', connector='Stock 76-pin',
         fits='1996–97 MX-5 Miata, manual and manual-swapped', status='Prototype', extra=''),
    dict(key='9900', years='1999–2000', title='Plug-in ECU 1999–2000', chassis='NB · 1.8', connector='Stock 64-pin',
         fits='1999–2000 MX-5 Miata, manual and manual-swapped', status='Prototype', extra=''),
    dict(key='0105', years='2001–05', title='Plug-in ECU 2001–05', chassis='NB · 1.8 VVT', connector='Stock 72-pin (3 rows)',
         fits='2001–05 MX-5 Miata, manual and manual-swapped', status='Prototype', extra=''),
]


def table(rows):
    return '<table>' + ''.join(f'<tr><th>{a}</th><td>{b}</td></tr>' for a, b in rows) + '</table>'


def ecu_body(y):
    return (f'<p>A rusEFI engine computer for the {y["years"]} Mazda MX-5 Miata ({y["chassis"]}). It fits the stock ECU '
            f'case and plugs into the stock harness connector. Two boards: the universal daughterboard that runs the '
            f'engine, and a motherboard made for your model year.</p>'
            + y['extra']
            + table([('Fits', y['fits']), ('Connector', y['connector'])] + COMMON
                    + [('Included', INCLUDED), ('Board only: you add', YOU_ADD), ('Complete kit adds', KIT_ADDS)]))


products = []
for y in YEARS:
    products.append(dict(handle=f'plug-in-ecu-{y["years"].replace("–", "-")}', title=y['title'], type='Plug-in ECU',
                         tags=f'ECU, {y["chassis"].split(" · ")[0]}, {y["years"]}',
                         body=ecu_body(y), key=y['key'],
                         image=f'render-assembly-{y["key"]}', status=y['status'],
                         variants=[dict(title=t, price=pr) for t, pr, _ in VARIANTS]))

HEAD = ['Handle', 'Title', 'Body (HTML)', 'Vendor', 'Type', 'Tags', 'Published', 'Option1 Name', 'Option1 Value',
        'Variant SKU', 'Variant Inventory Policy', 'Variant Fulfillment Service', 'Variant Price',
        'Variant Requires Shipping', 'Variant Taxable', 'Image Src', 'Image Alt Text', 'Gift Card', 'SEO Title',
        'SEO Description', 'Status']
with open(os.path.join(here, 'products.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(HEAD)
    for p in products:
        for i, (opt, price, sku) in enumerate(VARIANTS):
            if i == 0:
                w.writerow([p['handle'], p['title'], p['body'], '', p['type'], p['tags'], 'FALSE', 'Package', opt,
                            p['handle'] + sku, 'deny', 'manual', price, 'TRUE', 'TRUE', '', '', 'FALSE', p['title'],
                            f'{p["title"]}: a plug-in rusEFI engine computer for the Mazda MX-5 Miata.', 'draft'])
            else:   # further variants: handle plus the variant columns only (Shopify's import format)
                w.writerow([p['handle'], '', '', '', '', '', '', '', opt, p['handle'] + sku, 'deny', 'manual', price,
                            'TRUE', 'TRUE', '', '', '', '', '', ''])
json.dump(products, open(os.path.join(here, 'products.json'), 'w'), indent=1, ensure_ascii=False)
print(len(products), 'products')
