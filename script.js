const checkboxes = document.querySelectorAll('.checklist input[type="checkbox"]');

checkboxes.forEach((checkbox) => {
  checkbox.addEventListener("change", () => {
    const done = [...checkboxes].filter((item) => item.checked).length;
    document.title = `Quran Kareem (${done}/${checkboxes.length} done)`;
  });
});
