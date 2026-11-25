/* MSB Signs: editable message table. Uses existing HA helpers; no schedule writes. */
class MSBSignMessageGrid extends HTMLElement {
  setConfig(config) {
    this.config = config;
    if (!this.shadowRoot) this.attachShadow({mode: 'open'});
    this.shadowRoot.replaceChildren();
    const style = document.createElement('style');
    style.textContent = `
      :host {display:block} ha-card {padding:16px} h2 {margin:0 0 8px}
      p {color:var(--secondary-text-color);margin:8px 0 14px}
      .scroll {overflow-x:auto} table {border-collapse:collapse;width:100%;min-width:1300px}
      th {text-align:left;white-space:nowrap;background:var(--card-background-color);padding:10px 6px}
      td {padding:8px 6px;border-top:1px solid var(--divider-color)}
      input,select {box-sizing:border-box;width:100%;font:inherit;font-size:16px;
        color:var(--primary-text-color);background:var(--secondary-background-color);
        border:1px solid var(--divider-color);border-radius:5px;padding:10px 6px;min-height:44px}
      input[type=number] {width:75px} .text {min-width:190px} .rgb {min-width:115px}
      select {min-width:140px} .condition {min-width:175px}
      .drag {cursor:grab;touch-action:none;font:inherit;font-size:24px;min-height:44px;min-width:44px;
        color:var(--primary-text-color);background:transparent;border:1px solid var(--divider-color);border-radius:5px}
      .moves {display:flex;align-items:center;gap:3px;width:110px}
      .nudge {min-width:28px;min-height:40px;font-size:20px;color:var(--primary-text-color);
        background:transparent;border:1px solid var(--divider-color);border-radius:4px;cursor:pointer}
      .drag:active {cursor:grabbing} tr.moving {outline:2px solid var(--primary-color)}
      tr.drop-target {box-shadow:inset 0 3px var(--primary-color)}
      tr.disabled {opacity:.6} .error {color:var(--error-color);min-height:24px}
      td:first-child {font-weight:bold;width:35px} input:focus,select:focus {outline:2px solid var(--primary-color)}
    `;
    if(config.message_ids)style.textContent+=' .moves {display:none}';
    const card = document.createElement('ha-card');
    const title = document.createElement('h2'); title.textContent = 'Message grid';
    const help = document.createElement('p');
    help.textContent = 'Drag the dotted handle up or down; release on the marked row. The arrow buttons also move a row one place. Rows show rotation order; only eligible messages play on each sign. Use Arrow Up/Down on a focused handle for keyboard movement. Edits save when you leave a field or choose an option. Seconds 0 uses the default. Scroll sideways on a narrow screen. RGB fills show color with brightness boosted for visibility; stored pixel levels are unchanged. Gates/Traffic modes override the fixed background. Opening announcements in slots 7/9 are managed by the opening-week schedule.';
    this.feedback = document.createElement('div'); this.feedback.className = 'error';
    this.feedback.setAttribute('role','status');
    const scroll = document.createElement('div');scroll.className='scroll';
    const table=document.createElement('table');
    const head=table.createTHead().insertRow();
    const columns=[['Move'],['Slot'],['Sign','input_select','target'],['Show when','input_select','condition'],
      ['Top line','input_text','line1'],['Bottom line','input_text','line2'],
      ['Seconds','input_number','seconds'],
      ['Background mode','input_select','color_mode'],['Background RGB','input_text','background'],['Text RGB','input_text','text_color']];
    columns.forEach(([label])=>{const th=document.createElement('th');th.textContent=label;th.scope='col';head.append(th)});
    const body=table.createTBody();this.body=body;this.fields=[];this.rows=new Map();this.pendingOrder=null;
    for(const id of (config.message_ids||Array.from({length:17},(_,i)=>i+1))) {
      const row=body.insertRow();row.dataset.id=String(id);this.rows.set(id,row);
      const handle=document.createElement('button');handle.className='drag';handle.textContent='⠿';
      handle.title=`Move message slot ${id}`;handle.setAttribute('aria-label',`Move message slot ${id}; drag or use arrow keys`);
      // Use pointer capture for mouse AND touch. Native HTML dragging emits a
      // pointercancel event and was clearing the old drag state before drop.
      handle.draggable=false;
      handle.addEventListener('dragstart',event=>event.preventDefault());
      handle.addEventListener('pointerdown',event=>{
        if(event.button!==0||this.reordering||this.fields.some(f=>f.saving))return;
        event.preventDefault();this.dragId=id;this.dragTarget=id;
        this.dragStartY=event.clientY;this.dragMoved=false;
        row.classList.add('moving');handle.setPointerCapture(event.pointerId);
        handle.focus({preventScroll:true});
      });
      handle.addEventListener('pointermove',event=>{
        if(this.dragId!==id)return;
        if(Math.abs(event.clientY-this.dragStartY)<4&&!this.dragMoved)return;
        this.dragMoved=true;
        const target=this.rowAtY(event.clientY);
        if(!target)return;
        this.dragTarget=Number(target.dataset.id);
        for(const candidate of this.rows.values())candidate.classList.toggle('drop-target',candidate===target&&candidate!==row);
      });
      handle.addEventListener('pointerup',event=>{
        if(this.dragId!==id)return;
        const from=id,target=this.dragMoved?Number(this.rowAtY(event.clientY)?.dataset.id||this.dragTarget):id;
        this.clearDrag();
        if(handle.hasPointerCapture(event.pointerId))handle.releasePointerCapture(event.pointerId);
        if(from!==target)this.moveRow(from,target);
      });
      handle.addEventListener('pointercancel',()=>this.clearDrag());
      handle.addEventListener('lostpointercapture',()=>{if(this.dragId===id)this.clearDrag()});
      handle.addEventListener('keydown',event=>{
        if(!['ArrowUp','ArrowDown'].includes(event.key))return;
        event.preventDefault();this.nudgeRow(id,event.key==='ArrowUp'?-1:1);
      });
      const moves=document.createElement('div');moves.className='moves';moves.append(handle);
      for(const [label,step] of [['↑',-1],['↓',1]]) {
        const button=document.createElement('button');button.className='nudge';button.textContent=label;
        button.title=`Move message ${id} ${step<0?'up':'down'}`;button.setAttribute('aria-label',button.title);
        button.addEventListener('click',()=>this.nudgeRow(id,step));moves.append(button);
      }
      row.insertCell().append(moves);row.insertCell().textContent=id;
      for(const [label,domain,suffix] of columns.slice(2)) {
        const entity=`${domain}.msb_signs_message_${id}_${suffix}`;
        const field=document.createElement(domain==='input_select'?'select':'input');
        if(domain!=='input_select') field.type=domain==='input_number'?'number':'text';
        if(suffix==='line1'||suffix==='line2')field.className='text';
        if(suffix==='condition')field.className='condition';
        if(suffix==='background'||suffix==='text_color')field.className='rgb';
        field.setAttribute('aria-label',`Message ${id}: ${label}`);
        const entry={entity,domain,suffix,field,row};this.fields.push(entry);
        field.addEventListener('change',()=>this.save(entry));
        if(suffix==='background'||suffix==='text_color')field.addEventListener('input',()=>this.paintRGB(entry));
        row.insertCell().append(field);
      }
    }
    scroll.append(table);card.append(title,help,this.feedback,scroll);this.shadowRoot.append(style,card);
    if(this._hass)this.refresh();
  }
  set hass(hass) {this._hass=hass;if(this.fields)this.refresh()}
  refresh() {
    for(const entry of this.fields) {
      const {field,domain,entity,suffix,row}=entry;
      const state=this._hass.states[entity];
      field.disabled=!state||['unknown','unavailable'].includes(state.state)||entry.saving===true||this.reordering===true;
      if(!state)continue;
      // Never destroy a value while the operator is editing it.
      if(this.shadowRoot.activeElement===field||entry.saving)continue;
      if(domain==='input_select') {
        const options=state.attributes.options||[];
        if(JSON.stringify(options)!==entry.options) {
          field.replaceChildren(...options.map(value=>{const o=document.createElement('option');o.value=value;o.textContent=value;return o}));
          entry.options=JSON.stringify(options);
        }
      }
      if(domain==='input_number') {field.min=state.attributes.min;field.max=state.attributes.max;field.step=state.attributes.step||1}
      else if(domain==='input_text')field.maxLength=state.attributes.max||80;
      field.value=state.state;
      if(suffix==='background'||suffix==='text_color')this.paintRGB(entry);
      if(suffix==='target')row.classList.toggle('disabled',state.state==='Disabled');
    }
    this.sortRows();
  }
  rowAtY(y) {
    if(!this.body)return null;
    const rows=Array.from(this.body.rows);
    return rows.find(row=>{const box=row.getBoundingClientRect();return y>=box.top&&y<box.bottom})||null;
  }
  nudgeRow(id,step) {
    const ids=this.visibleIds(),target=ids[ids.indexOf(id)+step];
    if(target)return this.moveRow(id,target);
  }
  visibleIds() {return Array.from(this.body.rows,row=>Number(row.dataset.id))}
  clearDrag() {
    this.dragId=null;
    if(this.rows)for(const row of this.rows.values())row.classList.remove('moving','drop-target');
    this.sortRows();
  }
  orderValue(id) {
    const value=this._hass?.states[`input_number.msb_signs_message_${id}_order`]?.state;
    return Number.isFinite(Number(value))?Number(value):id;
  }
  sortRows() {
    if(!this.rows||this.dragId||this.reordering)return;
    // Do not move a row out from under an active text editor.
    if(this.shadowRoot.activeElement?.matches('input,select'))return;
    const live=Array.from(this.rows.keys()).sort((a,b)=>this.orderValue(a)-this.orderValue(b)||a-b);
    if(this.pendingOrder&&this.pendingOrder.every((id,index)=>this.orderValue(id)===index+1))this.pendingOrder=null;
    const ids=this.pendingOrder||live;
    if(ids.every((id,index)=>this.body.rows[index]?.dataset.id===String(id)))return;
    // Moving a focused handle can drop browser focus; restore it after sorting.
    const active=this.shadowRoot.activeElement;
    for(const id of ids)this.body.append(this.rows.get(id));
    active?.focus({preventScroll:true});
  }
  async moveRow(from,to) {
    if(this.config.message_ids||from===to||this.reordering||this.fields.some(f=>f.saving))return;
    const ids=this.visibleIds(),a=ids.indexOf(from),b=ids.indexOf(to);
    if(a<0||b<0)return;
    const original=new Map(ids.map(id=>[id,this.orderValue(id)]));
    ids.splice(a,1);ids.splice(b,0,from);
    this.reordering=true;this.pendingOrder=ids;
    for(const id of ids)this.body.append(this.rows.get(id));
    this.refresh();this.feedback.style.color='var(--secondary-text-color)';this.feedback.textContent='Saving rotation order…';
    const completed=[];
    try {
      // Existing HA helpers are independent writes. Save sequentially and restore
      // completed writes on error instead of reporting a partially saved move.
      for(let index=0;index<ids.length;index++) {
        const id=ids[index];if(original.get(id)===index+1)continue;
        await this._hass.callService('input_number','set_value',{entity_id:`input_number.msb_signs_message_${id}_order`,value:index+1});
        completed.push(id);
      }
      this.feedback.style.color='var(--success-color, #43a047)';this.feedback.textContent='Rotation order saved';
    } catch(error) {
      let restored=true;
      for(const id of completed.reverse()) {
        try {await this._hass.callService('input_number','set_value',{entity_id:`input_number.msb_signs_message_${id}_order`,value:original.get(id)})}
        catch {restored=false}
      }
      this.pendingOrder=null;this.feedback.style.color='var(--error-color)';
      this.feedback.textContent=restored?`Order could not be saved; previous order restored: ${error.message||error}`:
        'Order was only partly saved and could not be fully restored. Check the connection, refresh, and reorder again.';
    } finally {
      this.reordering=false;this.refresh();this.rows.get(from)?.querySelector('.drag')?.focus({preventScroll:true});
    }
  }
  // Normalize only the on-screen preview; never change the stored RGB levels.
  static rgbPreview(value) {
    const parts=String(value).split(',').map(v=>v.trim());
    if(parts.length!==3||parts.some(v=>!/^\d{1,3}$/.test(v)||Number(v)>255))return null;
    const raw=parts.map(Number),peak=Math.max(...raw);
    const rgb=peak?raw.map(v=>Math.round(v*255/peak)):raw;
    const linear=rgb.map(v=>{const c=v/255;return c<=0.04045?c/12.92:((c+0.055)/1.055)**2.4});
    const luminance=linear[0]*0.2126+linear[1]*0.7152+linear[2]*0.0722;
    return {background:`rgb(${rgb.join(',')})`,foreground:luminance>0.179?'#000000':'#ffffff'};
  }
  paintRGB(entry) {
    const {field,suffix,entity}=entry;
    const preview=MSBSignMessageGrid.rgbPreview(field.value);
    field.setCustomValidity(preview?'':'Enter three integers from 0 to 255, separated by commas.');
    field.style.background=preview?preview.background:'';
    field.style.color=preview?preview.foreground:'';
    field.style.borderColor=preview?'':'var(--error-color)';
    const modeEntity=entity.replace('input_text.','input_select.').replace(/_background$/,'_color_mode');
    const mode=this._hass?.states[modeEntity]?.state;
    field.title=preview?'Color preview boosted for visibility; raw pixel levels are unchanged.':'Invalid RGB: use three integers from 0 to 255.';
    if(suffix==='background'&&mode&&mode!=='Fixed')field.title+=` ${mode} mode overrides this fixed background.`;
  }
  async save(entry) {
    const {field,domain,entity}=entry;
    if(!field.reportValidity())return;
    const value=domain==='input_number'?Number(field.value):field.value;
    const data={entity_id:entity,[domain==='input_select'?'option':'value']:value};
    entry.saving=true;field.disabled=true;this.feedback.style.color='var(--secondary-text-color)';this.feedback.textContent='Saving…';
    try {
      await this._hass.callService(domain,domain==='input_select'?'select_option':'set_value',data);
      this.feedback.style.color='var(--success-color, #43a047)';this.feedback.textContent='Saved';
    } catch(error) {
      this.feedback.style.color='var(--error-color)';this.feedback.textContent=`Could not save ${entity}: ${error.message||error}`;
    } finally {entry.saving=false;field.disabled=false}
  }
  getCardSize() {return 12}
}
if(!customElements.get('msb-sign-message-grid'))customElements.define('msb-sign-message-grid',MSBSignMessageGrid);

/* Automatic Gates/Traffic palette: same validated editor as the message grid. */
class MSBSignColorGrid extends MSBSignMessageGrid {
  setConfig(config) {
    this.config=config;
    if(!this.shadowRoot)this.attachShadow({mode:'open'});
    this.shadowRoot.replaceChildren();
    const style=document.createElement('style');
    style.textContent=`
      :host {display:block} ha-card {padding:20px} h2 {margin:0 0 10px}
      p {color:var(--secondary-text-color);line-height:1.5}
      table {border-collapse:collapse;width:100%;max-width:1000px}
      th {text-align:left;padding:12px 10px} td {padding:12px 10px;border-top:1px solid var(--divider-color)}
      input {box-sizing:border-box;width:100%;min-width:140px;min-height:46px;
        font:inherit;font-size:18px;padding:10px;border:1px solid var(--divider-color);border-radius:6px}
      input:focus {outline:2px solid var(--primary-color)}
      .error {color:var(--error-color);min-height:24px} .scroll {overflow-x:auto}
      @media(max-width:600px) {.meaning {display:none} ha-card {padding:12px} td,th {padding:10px 6px}}
    `;
    const card=document.createElement('ha-card');
    const title=document.createElement('h2');title.textContent='Automatic background colors';
    const help=document.createElement('p');help.textContent='Edit RGB values below. Colors update as you type and save when you leave the field. Preview brightness is boosted for visibility; stored pixel levels stay unchanged.';
    this.feedback=document.createElement('div');this.feedback.className='error';this.feedback.setAttribute('role','status');
    const scroll=document.createElement('div');scroll.className='scroll';
    const table=document.createElement('table'),head=table.createTHead().insertRow();
    ['State','Used by','RGB color'].forEach((label,i)=>{const th=document.createElement('th');th.textContent=label;th.scope='col';if(i===1)th.className='meaning';head.append(th)});
    this.fields=[];
    const body=table.createTBody();
    for(const [key,label,meaning] of [
      ['open','Open','Gates mode — public hours'],
      ['closed','Closed','Gates mode — outside public hours'],
      ['light','Light traffic','Traffic mode — light'],
      ['moderate','Moderate traffic','Traffic mode — moderate'],
      ['busy','Busy traffic','Traffic mode — busy'],
      ['very_busy','Very busy traffic','Traffic mode — very busy']
    ]) {
      const row=body.insertRow();row.insertCell().textContent=label;
      const description=row.insertCell();description.textContent=meaning;description.className='meaning';
      const field=document.createElement('input');field.type='text';field.setAttribute('aria-label',`${label} RGB`);
      const entry={entity:`input_text.msb_signs_color_${key}`,domain:'input_text',suffix:'text_color',field,row};
      field.addEventListener('input',()=>this.paintRGB(entry));
      field.addEventListener('change',()=>this.save(entry));
      this.fields.push(entry);row.insertCell().append(field);
    }
    const note=document.createElement('p');note.textContent='These palette values apply to messages using Gates or Traffic background mode. They do not enable messages or change when signs run. Check the resulting colors on the physical signs.';
    scroll.append(table);card.append(title,help,this.feedback,scroll,note);this.shadowRoot.append(style,card);
    if(this._hass)this.refresh();
  }
  getCardSize(){return 7}
}
if(!customElements.get('msb-sign-color-grid'))customElements.define('msb-sign-color-grid',MSBSignColorGrid);
