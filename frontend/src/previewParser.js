// Deliberately narrow: offline preview must not guess advanced or destructive commands.
const aliases={house:'house|houses|home|homes|cottage|cottages|village',tree:'tree|trees|forest',lake:'lake|lakes|pond|ponds',river:'river|rivers|stream|streams',bridge:'bridge|bridges',road:'road|roads|path|paths',flower:'flower|flowers|garden',mountain:'mountain|mountains|hill|hills',tower:'tower|towers',castle:'castle|castles',rock:'rock|rocks|stone|stones'};
const words={a:1,an:1,one:1,two:2,three:3,four:4,five:5,six:6,seven:7,eight:8,nine:9,ten:10};
export function fallbackParser(text){
 const lower=text.trim().toLowerCase(),actions=[];
 const settings=lower.match(/^(?:make it |set )?(day|night)(?: with (rain|snow))?$/);
 if(settings){actions.push({action:'setting',key:'time',value:settings[1]});if(settings[2])actions.push({action:'setting',key:'weather',value:settings[2]})}
 else if(/^(?:make it )?(rain|snow)$/.test(lower))actions.push({action:'setting',key:'weather',value:lower.endsWith('rain')?'rain':'snow'});
 else if(/^(clear weather|no rain|no snow|stop raining|stop snowing)$/.test(lower))actions.push({action:'setting',key:'weather',value:'clear'});
 else for(const [type,nouns] of Object.entries(aliases)){
  const match=lower.match(new RegExp(`^(?:add|build|create|place|put|plant) (?:(${Object.keys(words).join('|')}|\\d+) )?(?:(red|blue|yellow|pink|purple|green|orange|white) )?(${nouns})$`));
  if(match){
   const count=words[match[1]]??Number(match[1]||1);
   const defaults={village:4,forest:6,garden:5};
   if(count>0)actions.push({action:'add',type,count:Math.min(16,defaults[match[3]]&&(!match[1]||['a','an'].includes(match[1]))?defaults[match[3]]:count),color:match[2]||null});
   break;
  }
 }
 return {text,actions,tokens:[],highlights:[],model:'browser-preview',grounding:'rules',warnings:['Python API is unavailable. Preview supports one simple add or weather/time instruction. Start the API for spatial, mixed, and removal commands.'],message:actions.length?'Used limited browser preview.':'This command needs the Python API; the scene was left unchanged.'};
}
