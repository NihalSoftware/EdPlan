import pathlib,json,re,collections,sys
out=pathlib.Path(__file__).resolve().parent
config=json.loads((out/'extraction-config.json').read_text(encoding='utf-8'));specs=config['specs']
tables=json.loads((out/'table-rows.json').read_text(encoding='utf-8'))
pages={n:json.loads((out/'ocr'/f'page-{n:03}.json').read_text(encoding='utf-8-sig')) for n in range(1,38)}
canonical={
'ENGL1110':'Composition I','ENGL1120':'Composition II','HIST1110':'United States History I','HIST1120':'United States History II',
'SPAN1110':'Spanish I','SPAN1120':'Spanish II','ARTH2110':'History of Art I','ARTH2120':'History of Art II',
'ARTS1610':'Drawing I','ARTS1616':'Drawing Comics and Sequential Art',
'BIOL2210C':'Human Anatomy and Physiology I','BIOL2225C':'Human Anatomy and Physiology II',
'BIOL2512':'Pathophysiology II','NMNC2310':'Health and Illness Concepts II','NMNC2410':'Health and Illness Concepts III',
'NMNC2320':'Professional Nursing Concepts I','NMNC2435':'Clinical Intensive I',
'RNBL1400':'Wind Turbine Climbing & Safety I'
}
manual={
(20,347):{'course_code':'BIOL1110C','course_name':'General Biology Lecture and Lab','credits':4},
(33,246):{'course_code':'FASC1210L','course_name':'Horseshoeing Laboratory I','credits':3},
(33,280):{'course_code':'FASC1310L','course_name':'Blacksmithing I','credits':3},
(33,378):{'course_code':'WELD1110','course_name':'Introduction to Welding Fundamentals','credits':3},
(37,1221):{'course_code':'RNBL1200','course_name':'OSHA 10','credits':1},
(37,1322):{'course_code':'RNBL1400','course_name':'Wind Turbine Climbing & Safety I','credits':1},
}
manual.update({(r['page'],r['y']):{k:v for k,v in r.items() if k not in ('page','y')} for r in config.get('manual',[])})
canonical.update(config.get('canonical',{}))
known_conflicts={
(23,'COMM1130'):'The Geology plan assigns 4 credits, but the general education catalog and other plans assign 3.',
(23,'GEOL1110'):'The plan names Physical Geology, while the general education list names Physical Geography.',
(24,'GEOL1110'):'The plan names Physical Geology, while the general education list names Physical Geography.',
(34,'ENGL2994'):'The plan shows 1 credit, but the general education listing states 3 credits.',
(18,'ARTS2850'):'The program calls ARTS2850 Art Foundry I, but the general education list calls it Ceramics II.',
(15,'ARTS1610'):'The same page labels ARTS1610 as both Drawing I and Drawing II.',
(30,'WELD1110','Applied Science Certificate'):'The source labels WELD1110 Composition I, conflicting with Welding Fundamentals elsewhere.',
(33,'ANSC1110'):'ANSC1110 is Horseshoeing Theory on page 82 but Animal Science Careers on page 74.',
(34,'MATH1130'):'The AAS plan assigns 3 credits, but the general education list and AA plan assign 4.',
}
code_re=re.compile(r'^([A-Z]{3,4})\s*([0-9]{3,4}[A-Z]?)$')
programs=[];courses=[];held=[];generic=[]
def is_boundary(row):
 c=row['code_text'].strip();t=row['title_text'].strip();full=row['text'].upper()
 return bool(c or re.search(r'SEMESTER CREDITS|TOTAL.*CREDITS|FIRST YEAR|SECOND YEAR|PREREQUISITES|ELECTIVES.*SELECT|NURSING.*TERM|CERTIFICATE|^CREDITS$|FIELD OF STUDY|ELECTIVE|COMM 1130 OR',full))
for spec in specs:
 n,name,degree,total,*bounds=spec;low,high=bounds if bounds else (0,1740)
 key=name+' | '+degree
 raw='\n'.join(l['text'] for l in pages[n]['lines'])
 selected=[r for r in tables[str(n)] if low<=r['y']<high]
 program={'program_name':name,'degree':degree,'total_credit_hours':total,'source_pdf_pages':[n],'source_printed_pages':[n+49],
 'source_requirements_text':'\n'.join(r['text'] for r in selected),'metadata_json':{'catalog_category':'Study plan','source_plan_name':name,'source_table_range_y':[low,high],'course_import_is_partial':True}}
 programs.append(program)
 year=None;term=None;heading=None;term_number=None;per_program=[]
 for idx,row in enumerate(selected):
  c=row['code_text'].strip();t=row['title_text'].strip();full=row['text']
  upper=full.upper()
  if 'FIRST YEAR' in upper:year=1;term=None;heading='First year';term_number=None;continue
  if 'SECOND YEAR' in upper:year=2;term=None;heading='Second year';term_number=None;continue
  if 'PREREQUISITES' in upper:year=None;term=None;heading='Program admission prerequisites';continue
  if c.upper() in ('FALL','SPRING'):
   term=c.title();heading=term
   if degree=='Applied Science Certificate':year=1
   continue
  if re.search(r'[1-4](?:st|nd|rd|th) Nursing',full,re.I):
   term=None;term_number=int(re.search(r'([1-4])(?:st|nd|rd|th)',full)[1]);heading=re.search(r'[1-4](?:st|nd|rd|th) Nursing.*',full,re.I)[0].replace('CREDITS','').strip();continue
  if 'ELECTIVES' in upper and 'SELECT' in upper:heading='Electives (select one)';term=None;year=None;continue
  corrected=manual.get((n,round(row['y'])))
  match=code_re.fullmatch(c.upper())
  if not match and corrected is None:
   if c and re.search(r'[A-Z]{3,}',c,re.I) and re.search(r'\d',c) and not re.search(r'YEAR|TERM|CERTIFICATE',upper):
    held.append({'program':key,'pdf_page':n,'printed_page':n+49,'source_row':full,'reason':'Course code is incomplete or contains ambiguous OCR characters'})
   elif re.search('ELECTIVE|FIELD OF STUDY|EXPERIENTIAL| OR ',full,re.I) and not re.search('CERTIFICATE',upper):
    generic.append({'program':key,'pdf_page':n,'source_row':full,'reason':'Selection/requirement slot retained as source text; no invented course code'})
   continue
  end=idx+1
  while end<len(selected) and not is_boundary(selected[end]) and not selected[end-1]['credit_text'].strip():end+=1
  block=selected[idx:end]
  source_text=' | '.join(r['text'] for r in block)
  code=corrected['course_code'] if corrected else ''.join(match.groups())
  if code=='ENGL2999' and not corrected and not any(r['credit_text'].strip() for r in block):
   corrected={'course_name':'Capstone Portfolio Course','credits':1,'course_code':code,'reference_credit_page':5}
  title=' '.join(r['title_text'] for r in block).strip()
  credit_cells=[r['credit_text'] for r in block if r['credit_text'].strip()]
  reason=known_conflicts.get((n,code,degree)) or known_conflicts.get((n,code))
  if corrected:
   title=corrected['course_name'];credits=corrected['credits'];evidence=('Visually verified credit in general education listing, PDF page 5 / printed page 54' if corrected.get('reference_credit_page') else 'Visual transcription from source page')
  else:
   evidence='OCR credit cell in the same bounded course row'
   if len(credit_cells)!=1 or not re.fullmatch(r'\d+(?:\.\d+)?|\.\d+',credit_cells[0]):reason=reason or 'No single explicit numeric credit cell in the course row'
   credits=float(credit_cells[0]) if len(credit_cells)==1 and re.fullmatch(r'\d+(?:\.\d+)?|\.\d+',credit_cells[0]) else None
  alternative_text=re.split('prerequisite',title,maxsplit=1,flags=re.I)[0]
  if re.search(r'\b(?:MATH|COMM|ARTS|FASC|BUSA|BCIS)\s*\d|\bor\b',alternative_text,re.I):
   if re.search(r'\b[A-Z]{3,4}\s+\d{3,4}',alternative_text) or 'elective' in alternative_text.lower():reason=reason or 'Source row combines alternatives rather than one unambiguous course'
  if credits is not None and not 0<credits<=12:reason=reason or 'Credit is outside the individual-course range'
  if not title:reason=reason or 'Missing course title'
  clean=re.sub(r'\s*\(Area[^)]*\)','',title,flags=re.I).strip()
  clean=re.sub(r'\s+or\s*$','',clean,flags=re.I)
  prerequisite_text=None
  if re.search('prerequisite',clean,re.I):
   clean,prerequisite_text=re.split('prerequisite',clean,maxsplit=1,flags=re.I)
   clean=clean.strip();prerequisite_text=prerequisite_text.strip()
  if code in canonical and not reason:clean=canonical[code]
  if re.search(r'\b(?:11|111|Ill|Ql|Q!)\b',clean):reason=reason or 'Unresolved OCR characters in course title'
  if reason:
   held.append({'program':key,'pdf_page':n,'printed_page':n+49,'source_row':source_text,'course_code':code,'reason':reason});continue
  elective=bool(re.search(r'\bor\b|elective|select one',alternative_text+' '+(heading or ''),re.I))
  item={'program_key':key,'course_code':code,'course_name':clean,'credits':credits,
   'recommended_year':None,'recommended_semester':None,'source_sequence':len(per_program)+1,
   'metadata_json':{'catalog_year':'2025-2026','source_pdf_page':n,'source_printed_page':n+49,'source_row':source_text,'source_credit_cells':credit_cells,'credit_evidence':evidence,'source_table_y':row['y'],
   'source_prerequisite_text':prerequisite_text,'source_heading':heading,'source_recommended_year':year,'source_recommended_semester':term,'source_term_number':term_number,'is_elective':elective,
   'course_import_is_partial':True,'scheduling_requires_complete_plan_review':True}}
  # Partial OCR coverage must not drive an automatic semester plan.
  if corrected:item['metadata_json']['visually_transcribed']=True
  if code in canonical:item['metadata_json']['title_standardized_from_visually_verified_catalog_rows']=True
  per_program.append(item)
 grouped=collections.defaultdict(list)
 for item in per_program:grouped[item['course_code']].append(item)
 for code,items in grouped.items():
  if len(items)>1:
   held.append({'program':key,'pdf_page':n,'printed_page':n+49,'course_code':code,'source_row':' || '.join(i['metadata_json']['source_row'] for i in items),'reason':'Repeated course code in study plan; repeat/alternative semantics need clarification'})
  else:courses.extend(items)
source=json.loads((out/'source.json').read_text())
source.update({'catalog_year':'2025-2026','catalog_year_evidence':'PDF Title metadata: (D)MCC-Catalog-2025-2026-05-(F).pdf','printed_page_range':[50,86],'is_current_catalog':False,'extraction_method':'Local Windows OCR with bounded table rows and visually checked transcriptions'})
issues=[
 {'program':'Agri-Business | Associate of Applied Science','pdf_page':25,'printed_page':74,'reason':'Semester totals 15+15+12+14 add to 56, but the catalog states 60 degree credits. Program held; authoritative total/curriculum needed.'},
 {'program':"Nurse’s Assistant | Certificate",'pdf_page':27,'printed_page':76,'total_credit_hours':5.5,'reason':'Fractional program total cannot fit integer database column; user requested to leave pending.'},
 {'program':'Phlebotomy | Certificate','pdf_page':28,'printed_page':77,'total_credit_hours':14.5,'reason':'Fractional program total cannot fit integer database column; user requested to leave pending.'},
 {'program':'Wind Energy Technology | Associate of Applied Science','pdf_page':36,'printed_page':85,'total_credit_hours':61.5,'reason':'Fractional program total cannot fit integer database column; user requested to leave pending.'},
 {'program':'Wind Energy Technology | Applied Science Certificate','pdf_page':37,'printed_page':86,'total_credit_hours':32.5,'reason':'Fractional program total cannot fit integer database column; user requested to leave pending.'},
 {'program':'General Business (AA), Animal Science (AAS), Public Administration/Law Enforcement (AAS)','pdf_page':8,'printed_page':57,'reason':'Overview names these options, but their complete curricula and specific totals are absent from the supplied excerpt.'}
]
dataset={'source':source,'institution':{'university_name':'Mesalands Community College','city':'Tucumcari','state':'New Mexico'},
'programs':programs,'courses':courses,'held_course_rows':held,'unresolved_requirement_slots':generic,'needs_clarification':issues,
'general_education_source_text':'\n\n'.join('PDF page '+str(n)+' / printed '+str(n+49)+'\n'+'\n'.join(l['text'] for l in pages[n]['lines']) for n in [4,5,6,7])}
assert len(programs)==26
assert len({(p['program_name'],p['degree']) for p in programs})==26
assert len({(c['program_key'],c['course_code']) for c in courses})==len(courses)
(out/'mesalands-import-data.json').write_text(json.dumps(dataset,ensure_ascii=False,indent=2),encoding='utf-8')
print('Programs:',len(programs),'Course rows:',len(courses),'Held rows:',len(held),'Generic requirement slots:',len(generic))
for p in programs:
 key=p['program_name']+' | '+p['degree']
 print('PDF',p['source_pdf_pages'][0],key,p['total_credit_hours'],'credits;',sum(c['program_key']==key for c in courses),'courses')
