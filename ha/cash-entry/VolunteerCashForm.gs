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
    const titles = ['Show date', 'Collection period', 'Dollars collected'];
    const items = form.getItems();
    if (items.some((item, index) => item.getTitle() !== titles[index])) {
      throw new Error('Review existing cash form questions before continuing.');
    }
    if (items.length < 1) form.addListItem().setTitle(titles[0]);
    if (items.length < 2) form.addListItem().setTitle(titles[1]);
    if (items.length < 3) form.addTextItem().setTitle(titles[2]);
    const questions = form.getItems();
    questions[0].asListItem().setChoiceValues(labels).setRequired(true);
    questions[1].asListItem().setChoiceValues(periods).setRequired(true);
    questions[2].asTextItem().setRequired(true).setValidation(FormApp.createTextValidation()
      .requireTextMatchesPattern('^[0-9]+([.][0-9]{1,2})?$')
      .setHelpText('Enter dollars and cents, for example 42.50 or 0.00.').build());
    form.setConfirmationMessage('Cash entry received. Submit another response for the next pickup.');
    if (!form.getDestinationId()) form.setDestination(FormApp.DestinationType.SPREADSHEET, book.getId());
    if (form.getDestinationId() !== book.getId()) throw new Error('Unexpected response workbook.');
    SpreadsheetApp.flush();
    // Identify this form's own sheet without relying on a generated tab number.
    const response = book.getSheets().find(sheet => {
      const url = sheet.getFormUrl();
      return url && FormApp.openByUrl(url).getId() === form.getId();
    });
    if (!response) throw new Error('Response tab pending. Run setup again.');
    const headers = response.getRange(1, 1, 1, response.getLastColumn()).getValues()[0];
    const tab = "'" + response.getName().replace(/'/g, "''") + "'!";
    const ranges = titles.map(title => {
      const index = headers.indexOf(title);
      if (index < 0) throw new Error('Missing response column: ' + title);
      const col = response.getRange(1, index + 1).getA1Notation().replace(/1$/, '');
      return tab + '$' + col + '$2:$' + col;
    });
    // Latest submission for this date and period is the correction. Zero stays numeric.
    // Populate empty cells only so existing manual entries and formulas survive reruns.
    dates.forEach((date, index) => {
      if (!(date instanceof Date)) return;
      periods.forEach((period, offset) => {
        const row = index + 3;
        const cell = park.getRange(row, 12 + offset);
        if (!cell.isBlank()) return;
        cell.setFormula('=IFNA(VALUE(XLOOKUP(1,ARRAYFORMULA((' + ranges[0] +
          '=("Show "&TEXT($B' + row + ',"yyyy-mm-dd")))*(' + ranges[1] + '="' +
          period + '"))),' + ranges[2] + ',NA(),0,-1)),"")');
      });
    });
    console.log('Set responder access and publish: ' + form.getEditUrl());
    console.log('Tablet form: ' + form.getPublishedUrl());
  } finally {
    lock.releaseLock();
  }
}
