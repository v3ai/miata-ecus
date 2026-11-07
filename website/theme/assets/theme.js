/* Mono theme: quantity steppers, variant picking, add to cart without leaving the page, cart quantity updates.
   Everything works without this file too: the forms post normally. */
(function () {
  'use strict';

  function formatMoney(cents, format) {
    var value = (cents / 100);
    var fmt = format || '${{amount}}';
    function withSep(n, decimals, thousands, decimal) {
      var parts = n.toFixed(decimals).split('.');
      parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, thousands);
      return parts.join(decimal);
    }
    return fmt.replace(/\{\{\s*(\w+)\s*\}\}/, function (_, key) {
      switch (key) {
        case 'amount_no_decimals': return withSep(value, 0, ',', '.');
        case 'amount_with_comma_separator': return withSep(value, 2, '.', ',');
        case 'amount_no_decimals_with_comma_separator': return withSep(value, 0, '.', ',');
        case 'amount_with_apostrophe_separator': return withSep(value, 2, "'", '.');
        default: return withSep(value, 2, ',', '.');
      }
    });
  }

  function setCartCount(count) {
    document.querySelectorAll('[data-cart-count]').forEach(function (el) {
      el.textContent = count;
      el.hidden = count === 0;
    });
  }

  /* scale a line of type to fill its box exactly (the footer's store name) */
  function fitText() {
    document.querySelectorAll('[data-fit-text]').forEach(function (box) {
      var span = box.firstElementChild;
      if (!span) return;
      box.style.fontSize = '';
      var size = parseFloat(getComputedStyle(box).fontSize);
      var width = box.clientWidth - parseFloat(getComputedStyle(box).paddingLeft) - parseFloat(getComputedStyle(box).paddingRight);
      if (span.offsetWidth > 0) box.style.fontSize = Math.min(size * width / span.offsetWidth, 400) + 'px';
    });
  }
  fitText();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitText);
  var fitTimer;
  window.addEventListener('resize', function () { clearTimeout(fitTimer); fitTimer = setTimeout(fitText, 100); });

  /* quantity steppers (product form and cart) */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-qty]');
    if (!btn) return;
    var input = btn.parentElement.querySelector('input[type="number"]');
    if (!input) return;
    var min = parseInt(input.min || '0', 10);
    var next = Math.max(min, (parseInt(input.value, 10) || 0) + parseInt(btn.dataset.qty, 10));
    if (String(next) === input.value) return;
    input.value = next;
    input.dispatchEvent(new Event('change', { bubbles: true }));
  });

  /* cart page: submit quantity changes */
  var cartForm = document.getElementById('cart');
  if (cartForm) {
    var timer;
    cartForm.addEventListener('change', function (e) {
      if (!e.target.matches('[data-cart-qty]')) return;
      clearTimeout(timer);
      timer = setTimeout(function () {
        var update = document.createElement('input');
        update.type = 'hidden'; update.name = 'update'; update.value = '1';
        cartForm.appendChild(update);
        cartForm.submit();
      }, 450);
    });
  }

  /* product page */
  document.querySelectorAll('[data-product-section]').forEach(function (section) {
    var jsonEl = section.querySelector('[data-product-json]');
    var form = section.querySelector('form[data-product-form]');
    if (!jsonEl || !form) return;
    var product = JSON.parse(jsonEl.textContent);
    var select = form.querySelector('[data-variant-select]');
    var button = form.querySelector('[data-add-button]');
    var errorBox = form.querySelector('[data-form-error]');
    var priceWrap = section.querySelector('[data-price-wrap]');
    var labels = section.dataset;

    function current() {
      var chosen = [];
      form.querySelectorAll('.variant-picker').forEach(function (fs) {
        var checked = fs.querySelector('input:checked');
        chosen.push(checked ? checked.value : null);
      });
      if (!chosen.length) return null;
      return product.variants.find(function (v) {
        return v.options.every(function (o, i) { return o === chosen[i]; });
      }) || null;
    }

    function markUnavailable() {
      /* strike through values that can't be bought with the other options as chosen */
      var pickers = form.querySelectorAll('.variant-picker');
      pickers.forEach(function (fs, index) {
        fs.querySelectorAll('input').forEach(function (input) {
          var chosen = [];
          pickers.forEach(function (other, j) {
            var c = other.querySelector('input:checked');
            chosen[j] = j === index ? input.value : (c ? c.value : null);
          });
          var ok = product.variants.some(function (v) {
            return v.available && v.options.every(function (o, i) { return o === chosen[i]; });
          });
          input.classList.toggle('is-unavailable', !ok);
        });
      });
    }

    function update() {
      var v = current();
      markUnavailable();
      if (!v) {
        button.disabled = true;
        button.textContent = labels.labelUnavailable;
        return;
      }
      select.value = v.id;
      button.disabled = !v.available;
      button.textContent = v.available ? labels.labelAdd : labels.labelSold;
      if (priceWrap) {
        var html = '';
        if (v.compare_at_price && v.compare_at_price > v.price) {
          html += '<s>' + formatMoney(v.compare_at_price, labels.moneyFormat) + '</s>';
        }
        html += formatMoney(v.price, labels.moneyFormat);
        priceWrap.innerHTML = '<span class="price">' + html + '</span>';
      }
      var url = new URL(window.location.href);
      url.searchParams.set('variant', v.id);
      window.history.replaceState({}, '', url.toString());
    }

    form.addEventListener('change', function (e) {
      if (e.target.matches('.variant-picker input')) update();
    });
    if (form.querySelector('.variant-picker')) markUnavailable();

    form.addEventListener('submit', function (e) {
      if (!window.fetch) return;
      e.preventDefault();
      errorBox.hidden = true;
      button.disabled = true;
      fetch(window.Shopify && Shopify.routes ? Shopify.routes.root + 'cart/add.js' : '/cart/add.js', {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        body: new FormData(form)
      })
        .then(function (r) { return r.json().then(function (body) { return { ok: r.ok, body: body }; }); })
        .then(function (res) {
          if (!res.ok) throw new Error(res.body.description || res.body.message || 'Error');
          button.textContent = labels.labelAdded;
          return fetch((window.Shopify && Shopify.routes ? Shopify.routes.root : '/') + 'cart.js')
            .then(function (r) { return r.json(); })
            .then(function (cart) { setCartCount(cart.item_count); });
        })
        .catch(function (err) {
          errorBox.textContent = err.message;
          errorBox.hidden = false;
        })
        .finally(function () {
          setTimeout(function () {
            var v = current() || product.variants.find(function (x) { return String(x.id) === select.value; });
            button.disabled = v ? !v.available : false;
            button.textContent = v && !v.available ? labels.labelSold : labels.labelAdd;
          }, 1600);
        });
    });
  });
})();
