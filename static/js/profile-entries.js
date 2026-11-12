document.querySelectorAll('[data-entry-collection]').forEach(collection => {
  const addButton = collection.querySelector('[data-add-entry]');
  const forms = collection.querySelector('[data-entry-forms]');
  const template = collection.querySelector('[data-entry-template]');
  const total = collection.querySelector(`[name="${collection.dataset.prefix}-TOTAL_FORMS"]`);
  if (!addButton || !forms || !template || !total) return;
  addButton.hidden = false;
  addButton.addEventListener('click', () => {
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
    const field = content.querySelector('input:not([type="hidden"]):not([type="checkbox"]), textarea');
    forms.append(content);
    total.value = String(index + 1);
    field?.focus();
  });
});
