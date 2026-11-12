document.querySelectorAll('[data-entry-collection]').forEach(collection => {
  const addButton = collection.querySelector('[data-add-entry]');
  const forms = collection.querySelector('[data-entry-forms]');
  const template = collection.querySelector('[data-entry-template]');
  const total = collection.querySelector(`[name="${collection.dataset.prefix}-TOTAL_FORMS"]`);
  if (!addButton || !forms || !template || !total) return;
  const rows = () => [...forms.children].filter(row => row.matches('[data-entry-form]'));
  const isUnused = row => row.dataset.existing === 'false'
    && row.dataset.hasErrors !== 'true'
    && !row.querySelector('input[type="checkbox"]:checked')
    && [...row.querySelectorAll('input:not([type="hidden"]):not([type="checkbox"]), textarea, select')]
      .every(field => !field.value.trim());
  const firstField = row => row.querySelector('input:not([type="hidden"]):not([type="checkbox"]), textarea');
  rows().filter(isUnused).forEach(row => { row.hidden = true; });
  addButton.hidden = false;
  addButton.addEventListener('click', () => {
    const unused = rows().find(isUnused);
    if (unused) {
      unused.hidden = false;
      firstField(unused)?.focus();
      return;
    }
    const index = Number(total.value);
    if (!Number.isSafeInteger(index) || index < 0 || index >= 1000) return;
    const content = template.content.cloneNode(true);
    content.querySelectorAll('*').forEach(element => {
      for (const attribute of [...element.attributes]) {
        if (attribute.value.includes('__prefix__')) {
          element.setAttribute(attribute.name, attribute.value.replaceAll('__prefix__', String(index)));
        }
      }
    });
    const field = firstField(content);
    forms.append(content);
    total.value = String(index + 1);
    field?.focus();
  });
});
