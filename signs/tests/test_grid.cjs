const {JSDOM}=require('jsdom'),fs=require('fs'),assert=require('assert');
(async()=>{
 const dom=new JSDOM('<html><body></body></html>',{runScripts:'outside-only'}),w=dom.window;
 w.eval(fs.readFileSync(require('path').join(__dirname,'../www/msb-sign-message-grid.js'),'utf8'));
 const states={};
 for(let id=1;id<=17;id++)for(const [domain,keys] of [['input_number',['order','seconds']],['input_text',['line1','line2','background','text_color']],['input_select',['target','condition','color_mode']]])for(const key of keys){
 const value=key==='order'?String(id):key==='seconds'?'7':key==='target'?'Both':key==='condition'?'Pre-show':key==='color_mode'?'Fixed':key==='background'?'0,0,12':key==='text_color'?'100,100,100':`Message ${id}`;
 states[`${domain}.msb_signs_message_${id}_${key}`]={state:value,attributes:{min:key==='order'?1:0,max:domain==='input_text'?80:99,step:1,options:key==='target'?['Both','Disabled']:key==='condition'?['Pre-show']:['Fixed']}};
 }
 states['input_number.msb_signs_message_8_order'].state='6';states['input_number.msb_signs_message_9_order'].state='7';
 const card=w.document.createElement('msb-sign-message-grid');card.setConfig({});w.document.body.append(card);
 let calls=0,failAt=0;
 const hass={states,callService:async(d,s,data)=>{calls++;if(calls===failAt)throw Error('simulated network failure');states[data.entity_id].state=String(data.value??data.option);card.hass=hass}};
 card.hass=hass;
 const ids=()=>Array.from(card.visibleIds());
 assert.deepEqual(ids(),[1,2,3,4,5,6,8,7,9,10,11,12,13,14,15,16,17]);
 // Simulate captured pointer events with row geometry, including the native
 // drag cancellation regression: native dragstart must be prevented.
 const handle=card.rows.get(8).querySelector('.drag');
 handle.setPointerCapture=()=>{};handle.hasPointerCapture=()=>true;handle.releasePointerCapture=()=>{};
 for(const [i,id] of ids().entries())card.rows.get(id).getBoundingClientRect=()=>({top:i*60,bottom:(i+1)*60});
 const pointer=(name,y)=>{const e=new w.Event(name,{bubbles:true,cancelable:true});Object.assign(e,{button:0,pointerId:1,clientY:y});handle.dispatchEvent(e);return e};
 assert.equal(handle.draggable,false);
 const native=new w.Event('dragstart',{cancelable:true});handle.dispatchEvent(native);assert(native.defaultPrevented);
 pointer('pointerdown',390);assert.equal(card.dragId,8);
 pointer('pointermove',330);assert.equal(card.dragTarget,6);
 pointer('pointerup',330);
 while(card.reordering)await new Promise(r=>setTimeout(r,0));
 assert.deepEqual(ids(),[1,2,3,4,5,8,6,7,9,10,11,12,13,14,15,16,17]);
 assert(ids().every((id,i)=>Number(states[`input_number.msb_signs_message_${id}_order`].state)===i+1));
 assert.equal(card.feedback.textContent,'Rotation order saved');
 // Keyboard move, with stable slot identity after reconfiguration.
 card.rows.get(8).querySelector('.drag').dispatchEvent(new w.KeyboardEvent('keydown',{key:'ArrowUp',bubbles:true}));
 while(card.reordering)await new Promise(r=>setTimeout(r,0));
 assert.equal(ids()[4],8);
 await card.nudgeRow(8,1);assert.equal(ids()[5],8);await card.nudgeRow(8,-1);
 card.setConfig({});card.hass=hass;assert.equal(ids()[4],8);
 // Fail after one successful write: rollback must restore all previous numbers.
 const original=JSON.stringify(states);failAt=calls+2;await card.moveRow(8,1);
 assert.equal(JSON.stringify(states),original);assert.equal(ids()[4],8);
 assert(card.feedback.textContent.includes('previous order restored'));
 assert.equal(card.rows.get(8).querySelector('input.rgb').style.background,'rgb(0, 0, 255)');
 const palette=w.document.createElement('msb-sign-color-grid');palette.setConfig({});
 assert.equal(palette.fields.length,6);palette.hass=hass;
 const advertising=w.document.createElement('msb-sign-message-grid');advertising.setConfig({message_ids:[8,9,10,11]});advertising.hass=hass;assert.deepEqual(Array.from(advertising.visibleIds()),[8,9,10,11]);const before=calls;await advertising.moveRow(8,9);assert.equal(calls,before);
 console.log('Passed: pointer drag mouse/touch path, native drag disabled, initial sorting with ties, drag/drop event handlers, unique saved order, keyboard movement, reload persistence, partial-failure rollback, RGB previews, and Colors card.');
})().catch(e=>{console.error(e);process.exit(1)});
