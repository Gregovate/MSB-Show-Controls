// Run once from a new .gs file in the Show Stats workbook's Apps Script project.
// The returned form stays unpublished until its owner selects the tablet responder.
function NightlyCashForm() {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const book = SpreadsheetApp.getActiveSpreadsheet();
    const park = book.getSheetByName('Park Data 2026');
    const periods = ['Cash 5:00-6:00', 'Cash 6:00-7:00', 'Cash 7:00-8:00',
                     'Cash 8:00-9:00', 'Cash After 9 PM'];
    if (!park || park.getRange('L2:P2').getValues()[0].join('|') !== periods.join('|')) {
      throw new Error('Check the Park Data 2026 cash headers before setup.');
    }
    const dates = park.getRange('B3:B37').getValues().flat();
    const labels = dates.filter(date => date instanceof Date).map(date =>
      'Show ' + Utilities.formatDate(date, book.getSpreadsheetTimeZone(), 'yyyy-MM-dd'));
    const props = PropertiesService.getScriptProperties();
    const key = 'MSB_2026_VOLUNTEER_CASH_FORM';
    const id = props.getProperty(key);
    const title = 'ParkDonations';
    const form = id ? FormApp.openById(id) : FormApp.create(title, false);
    if (id && form.getTitle() !== title) form.setTitle(title);
    if (!id) props.setProperty(key, form.getId());
    const noteTitle = 'Nightly note';
    const amountTitles = periods.map(period => period.replace(/^Cash /, 'Hourly Total Amount '));
    const titles = ['Show date', ...amountTitles, noteTitle];
    // The original form used a period selector and a single amount. Remove
    // those two setup questions only while the original form is still unused.
    const obsolete = form.getItems().filter(item =>
      ['Collection period', 'Dollars collected'].includes(item.getTitle()));
    if (obsolete.length && form.getResponses().length) {
      throw new Error('Existing hourly responses detected. Stop before changing questions.');
    }
    obsolete.reverse().forEach(item => form.deleteItem(item));
    const items = form.getItems();
    if (items.some((item, index) => item.getTitle() !== titles[index] &&
        !(index > 0 && index <= periods.length && item.getTitle() === periods[index - 1]))) {
      throw new Error('Review existing cash form questions before continuing.');
    }
    const day = items[0] ? items[0].asListItem() : form.addListItem().setTitle(titles[0]);
    day.setChoiceValues(labels).setRequired(true);
    const money = FormApp.createTextValidation()
      .requireTextMatchesPattern('^[0-9]+([.][0-9]{1,2})?$')
      .setHelpText('Enter dollars and cents, for example 42.50 or 0.00.').build();
    amountTitles.forEach((title, index) => {
      const item = items[index + 1];
      const question = item ? item.asTextItem() : form.addTextItem();
      question.setTitle(title).setRequired(false).setValidation(money);
    });
    const noteItem = items[periods.length + 1];
    const note = noteItem ? noteItem.asParagraphTextItem() : form.addParagraphTextItem().setTitle(noteTitle);
    note.setRequired(false).setHelpText('Anything unusual about tonight’s count? For example, two buckets were counted together.');
    form.setDescription('For each period, enter one total for bills, coins, and checks combined. Leave an uncounted period blank. Enter 0 for a confirmed zero. To correct a period, submit its updated total.');
    form.setConfirmationMessage('Hourly totals received.');
    // Google throws when a newly created form has no response destination.
    let destinationId;
    try {
      destinationId = form.getDestinationId();
    } catch (error) {
      if (!/form currently has no response destination/i.test(error.message)) throw error;
    }
    if (!destinationId) {
      form.setDestination(FormApp.DestinationType.SPREADSHEET, book.getId());
      destinationId = form.getDestinationId();
    }
    if (destinationId !== book.getId()) throw new Error('Unexpected response workbook.');
    SpreadsheetApp.flush();
    // Identify this form's own sheet without relying on a generated tab number.
    const response = book.getSheets().find(sheet => {
      const url = sheet.getFormUrl();
      return url && FormApp.openByUrl(url).getId() === form.getId();
    });
    if (!response) throw new Error('Response tab pending. Run setup again.');
    const headers = response.getRange(1, 1, 1, response.getLastColumn()).getValues()[0];
    const tab = "'" + response.getName().replace(/'/g, "''") + "'!";
    const ranges = titles.slice(0, 1 + periods.length).map((title, position) => {
      // Linked response headers can retain the original question title.
      const matches = headers.map((header, i) => header === title ||
        (position > 0 && header === periods[position - 1]) ? i : -1).filter(i => i >= 0);
      if (matches.length > 1) throw new Error('Ambiguous response column: ' + title);
      const index = matches.length ? matches[0] : -1;
      if (index < 0) throw new Error('Missing response column: ' + title);
      const col = response.getRange(1, index + 1).getA1Notation().replace(/1$/, '');
      // Forms inserts response rows. Whole-column references include the first submission.
      return tab + '$' + col + ':$' + col;
    });
    // Latest submission for this date and period is the correction. Zero stays numeric.
    // Populate empty cells only so existing manual entries and formulas survive reruns.
    dates.forEach((date, index) => {
      if (!(date instanceof Date)) return;
      periods.forEach((period, offset) => {
        const row = index + 3;
        const cell = park.getRange(row, 12 + offset);
        const existing = cell.getFormula();
        const legacy = '=IFNA(VALUE(XLOOKUP(1,ARRAYFORMULA((' + tab + '$B$2:$B=("Show "&TEXT($B' +
          row + ',"yyyy-mm-dd")))*(' + tab + '$C$2:$C="' + period + '"))),' +
          tab + '$D$2:$D,NA(),0,-1)),"")';
        const amounts = ranges[offset + 1];
        const formula = '=IFNA(VALUE(XLOOKUP(1,ARRAYFORMULA((' + ranges[0] +
          '=("Show "&TEXT($B' + row + ',"yyyy-mm-dd")))*(' + amounts +
          '<>"")),' + amounts + ',NA(),0,-1)),"")';
        if (cell.isBlank() || existing === legacy || existing === legacy.replace('"))),', '")),')) cell.setFormula(formula);
      });
    });
    console.log('Set responder access and publish: ' + form.getEditUrl());
    console.log('Tablet form: ' + form.getPublishedUrl());
  } finally {
    lock.releaseLock();
  }
}
