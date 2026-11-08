document.querySelectorAll('[data-copy]').forEach(button => {
  button.addEventListener('click', async () => {
    const source = document.getElementById(button.dataset.copy);
    const value = source.textContent;
    let copied = false;
    try {
      await Promise.race([
        navigator.clipboard.writeText(value),
        new Promise((resolve, reject) => setTimeout(() => reject(new Error('clipboard timeout')), 1000))
      ]);
      copied = true;
    } catch (error) {
      const range = document.createRange();
      range.selectNodeContents(source);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      button.textContent = '選択済み';
      let hint = document.getElementById('copy-hint-' + button.dataset.copy);
      if (!hint) {
        hint = document.createElement('p');
        hint.id = 'copy-hint-' + button.dataset.copy;
        hint.className = 'mini-note';
        (button.closest('.copy-row') || button).insertAdjacentElement('afterend', hint);
      }
      hint.textContent = '全文を選択しました。Ctrl+C（Macは⌘C）、スマホは選択メニューのコピーを使ってください。';
    }
    document.getElementById('copy-announcer').textContent = copied
      ? '全文をコピーしました。'
      : '全文を選択しました。PCはCtrl+C（Macは⌘C）、スマホは選択メニューのコピーを使ってください。';
    if (copied) {
      const previous = button.textContent;
      button.textContent = 'コピーしました';
      setTimeout(() => { button.textContent = previous; }, 1800);
    }
  });
});
