"""Extract clear SIPI course rows from preserved digital PDF text.
Source totals and choices are preserved. No synthetic courses, credits or schedules.
"""
import collections,json,pathlib,re
HERE=pathlib.Path(__file__).resolve().parent
START=re.compile(r'^([A-Za-z]{2,4})\s*(\d{3,4}[A-Za-z]?(?:/L|/\d{3,4})?)\b')
CODE=re.compile(r'^[A-Z]{2,4}\d{3,4}[A-Za-z]?(?:/L)?$')
HEAD=re.compile(r'^(?:Area\s|Associated Essential|Course ID|Couse ID|General Education|Flexible Credits|Program-Specific|PROGRAM-SPECIFIC|Technical[/ /]|Approved Electives|Electives approved|The required courses|sequences, co|For AAS|competency requirements|requirements\.|TOTAL CREDIT|Choose \d|List electives|Use this section|unless permitted|or institutional|meeting essential)')
def clean_lines(text):
    return [l.strip() for l in text.replace('\r','').split('\n') if l.strip() and not re.match(r'^(?:2026-2027 Academic Catalog|Page \| \d+)',l.strip())]
def parse_credit(raw):
    if re.fullmatch(r'\d+(?:\.\d+)?T?',raw):return float(raw.rstrip('T'))
    if re.fullmatch(r'\d+/\d+',raw):return sum(float(n) for n in raw.split('/'))
    if re.fullmatch(r'\d+\s+\(\d+/\d+\)',raw):
        total=float(raw.split()[0]);assert total==sum(float(n) for n in re.findall(r'\d+',raw)[1:]);return total
    return None
def extract_blocks(lines,page):
    result=[];current=None;section='required'
    def finish():
        nonlocal current
        if current:result.append(current)
        current=None
    for line in lines:
        if HEAD.match(line):
            finish()
            if line.startswith('Approved Electives'):section='approved_elective'
            continue
        if re.match(r'^(?:ANY\b|GIT ANY\b|COSC/GIT/ENGR\b|Elective$|Science Elective:|\*Students|However,)',line):
            finish();continue
        m=START.match(line)
        if m or re.fullmatch(r'[A-Z]{2,4}',line):
            finish();current={'pdf_page':page,'printed_page':page+60,'source_lines':[line],'section':section}
        elif current:current['source_lines'].append(line)
    finish();return result
def blocked_identity(name,degree,code):
    if code in {'ENGL1110','ENGL2110'} and (name=='Accounting' or name=='Business Administration'):
        return 'Conflicting English course code between required curriculum and suggested sequence.'
    if name=='Business Administration' and degree=='Associate of Applied Science' and code in {'ENTR2110','ENTR2210'}:
        return 'Small Business Management has conflicting ENTR codes.'
    if name=='Business Administration' and degree=='Certificate' and code in {'BUED125','BUSA1180','BUSA2230','BUSA2320'}:
        return 'Business Math/Human Relations course code conflicts with suggested sequence.'
    if name=='Culinary Arts & Sciences' and code in {'ENGL1130','CULN1235L','CULN1235','BUSA1110','BUSN1110'}:
        return 'Course identity differs between the formal curriculum, sequence or other catalog entries.'
    if code=='SPAN1110':return 'SPAN 1110 is 3 credits here but 4 credits in other SIPI curricula.'
    if code=='COSC145':return 'COSC 145 title conflicts across SIPI program listings.'
    if name=='Optical Laboratory Technology' and code in {'HLED1120','HLED1110'}:
        return 'First-aid code and credits conflict or are missing in the source.'
    return None
def build():
    config=json.loads((HERE/'extraction-config.json').read_text(encoding='utf-8'))
    pages=json.loads((HERE/'catalog-pages.json').read_text(encoding='utf-8'))
    data={k:config[k] for k in ('institution','source','held_programs','needs_clarification')}
    data.update(programs=[],courses=[],held_course_rows=[],unresolved_requirement_slots=[])
    for name,degree,total,cip,first,last,marker in config['specs']:
        key=name+' | '+degree;regions=[];blocks=[]
        for page in range(first,last+1):
            text=pages[page-1].replace('\r','')
            if page==first:text=text[text.index(marker):]
            if page==last:text=text[:text.index('TOTAL CREDIT HOURS REQUIRED:')]
            lines=clean_lines(text);regions.append({'source_pdf_page':page,'source_printed_page':page+60,'source_text':'\n'.join(lines)})
            blocks.extend(extract_blocks(lines,page))
            for line in lines:
                if re.match(r'^[A-Z]{2,4}/L\d',line):
                    data['held_course_rows'].append({'program_key':key,'pdf_page':page,'printed_page':page+60,'source_lines':[line],'course_code':line.split()[0],'reason':'Identifier is printed in a different layout (BIOL/L1110); confirm the canonical code.'})
        program={'program_name':name,'degree':degree,'total_credit_hours':total,
           'source_pdf_pages':list(range(first,last+1)),'source_printed_pages':list(range(first+60,last+61)),
           'source_requirements_text':'\n\n'.join(f"PDF {s['source_pdf_page']} / printed {s['source_printed_page']}:\n{s['source_text']}" for s in regions),
           'metadata_json':{'cip_code':cip,'source_regions':regions,'course_import_is_partial':True,'planning_ready':False,
              'import_scope':'Only unambiguous course identities and credit cells from the formal curriculum; no suggested schedules assigned.',
              'catalog_institution_name':config['institution']['catalog_institution_name']}}
        if name=='Early Childhood Education' and degree=='Associate of Arts':
            program['metadata_json']['non_course_requirements_source_text']='\\n'.join(clean_lines(pages[26].split('General Education Required Courses')[0]))
            program['metadata_json']['non_course_requirements_source_printed_page']=87
        data['programs'].append(program)
        seen=set()
        for seq,block in enumerate(blocks,1):
            text=' '.join(block['source_lines']);m=START.match(text)
            if m is None:
                data['held_course_rows'].append({'program_key':key,**block,'course_code':text.split()[0],'reason':'Department or sequence without a supported single course identifier.'});continue
            prefix,number=m.groups();code=prefix.upper()+number
            body=text[m.end():].strip()
            reason=blocked_identity(name,degree,code)
            if not CODE.fullmatch(code):reason=reason or 'Combined sequence or unsupported course identifier.'
            # Split title/credit at the last small numeric cell; later prerequisite IDs are hundreds/thousands.
            credits=list(re.finditer(r'(?<!\S)(\d+(?:\.\d+)?(?:T|\s+\(\d+/\d+\)|/\d+)?)(?=\s|$)',body))
            choices=[c for c in credits if (parse_credit(c.group(1)) or 999)<=12]
            found=choices[-1] if choices else None
            if not found:reason=reason or 'Missing or ambiguous course-credit cell.'
            title=body[:found.start()].strip() if found else body
            tail=body[found.end():].strip() if found else ''
            rawcredit=found.group(1) if found else ''
            if re.search(r'\b(?:or|OR|substitute|substitution|elective)\b',title) or re.search(r'[A-Z]{2,4}\s*\d{3,4}',title):
                reason=reason or 'Choice or substitution is not a single unambiguous course title.'
            if tail and not re.fullmatch(r'(?:[A-Z]{2,4}\s*\d{3,4}[A-Z]?,?\s*)+|Completion of Degree Requirements.*',tail) and not re.fullmatch(r'Acceptance (?:to|into) [Pp]rogram',tail):
                reason=reason or 'Unresolved continuation or credit/prerequisite layout.'
            if re.search(r'\b(?:ANY|GIT ANY|TOTAL CREDIT HOURS)\b',title):reason=reason or 'Generic requirement text was not a course title.'
            if not title:reason=reason or 'Missing course title.'
            if code in seen:reason=reason or 'Duplicate source course identifier in the same program.'
            if reason:
                data['held_course_rows'].append({'program_key':key,**block,'course_code':code,'reason':reason});continue
            seen.add(code);credit=parse_credit(rawcredit)
            metadata={**block,'source_row':text,'source_credit_cell':rawcredit,'credit_evidence':'Numeric credit cell in the supplied catalog formal requirements.',
               'source_section':block['section'],'is_elective':block['section']=='approved_elective','prerequisite_corequisite_text':tail,
               'includes_laboratory':code.endswith('/L'),'components_are_source_grouping':code.endswith('/L'),
               'course_import_is_partial':True,'planning_ready':False}
            if rawcredit.endswith('T'):metadata['credit_annotation']='T (preserved as printed; not assigned an inferred meaning)'
            data['courses'].append({'program_key':key,'course_code':code,'course_name':title,'credits':int(credit) if credit.is_integer() else credit,
               'lecture_hours':None,'lab_hours':None,'recommended_year':None,'recommended_semester':None,'source_sequence':seq,'metadata_json':metadata})
        # Retain all non-course requirements in the full source, including empty-code elective slots.
        for region in regions:
            for line in region['source_text'].splitlines():
                if re.search(r'\b(?:ANY|Any|Choose|choose|Elective|elective|OR|or)\b',line) and not HEAD.match(line):
                    data['unresolved_requirement_slots'].append({'program_key':key,'source_pdf_page':region['source_pdf_page'],'source_printed_page':region['source_printed_page'],'source_text':line})
    for group in config.get('choice_groups',[]):
        assert group['source_text'] in pages[group['source_pdf_page']-1]
        for course in data['courses']:
            if course['program_key']==group['program_key'] and course['course_code'] in group['course_codes']:
                course['metadata_json'].update(is_elective=True,requirement_choice_group=group)
        for program in data['programs']:
            if program['program_name']+' | '+program['degree']==group['program_key']:
                program['metadata_json'].setdefault('requirement_choices',[]).append(group)
    return data
def validate(data):
    assert data['source']['sha256']=='6eaf3f400e5424ff5dfd9414a3b36f7304b932f0915d18b20041f08af938a205'
    assert len(data['programs'])==15 and len(data['held_programs'])==5
    keys={p['program_name']+' | '+p['degree'] for p in data['programs']}
    assert len(keys)==15 and all(type(p['total_credit_hours']) is int and p['total_credit_hours']>0 for p in data['programs'])
    assert len(data['courses'])==187
    pages=json.loads((HERE/'catalog-pages.json').read_text(encoding='utf-8'))
    seen=set();credit_values=collections.defaultdict(set)
    for c in data['courses']:
        assert c['program_key'] in keys and CODE.fullmatch(c['course_code']) and 0<c['credits']<=12
        assert c['recommended_year'] is None and c['recommended_semester'] is None
        assert c['lecture_hours'] is None and c['lab_hours'] is None
        assert c['credits']==parse_credit(c['metadata_json']['source_credit_cell'])
        assert c['metadata_json']['printed_page']==c['metadata_json']['pdf_page']+60
        assert all(line in clean_lines(pages[c['metadata_json']['pdf_page']-1]) for line in c['metadata_json']['source_lines'])
        assert not re.search(r'\b(?:ANY|TOTAL CREDIT HOURS)\b',c['course_name'])
        credit_values[c['course_code']].add(c['credits'])
        assert (c['program_key'],c['course_code']) not in seen;seen.add((c['program_key'],c['course_code']))
    assert all(len(v)==1 for v in credit_values.values())
    indexed={(c['program_key'],c['course_code']):c for c in data['courses']}
    labs=[c for c in data['courses'] if c['program_key']=='Natural Resources Management | Associate of Applied Science' and c['course_code'] in {'NATR201/L','RGSC2110/L','FWCE2110/L'}]
    assert len(labs)==3 and all(c['metadata_json']['is_elective'] and c['metadata_json']['requirement_choice_group']['choose_count']==2 for c in labs)
    assert indexed[('Pre-Engineering | Associate of Science','ENGR211/L')]['credits']==4
    assert indexed[('Culinary Arts & Sciences | Associate of Applied Science','CULN2999')]['credits']==2
    assert indexed[('Optical Laboratory Technology | Certificate of Completion','OPTI101')]['metadata_json']['prerequisite_corequisite_text']=='Acceptance into program'
    assert indexed[('Geospatial Information Technology | Certificate','GIT201')]['course_name']=='Principles and Theory of GIS & GPS Applied'
    assert not any(c['course_code']=='SPAN1110' for c in data['courses'])
    cons=[c for c in data['courses'] if c['program_key'].startswith('Conservation and Resource Protection |')]
    assert len(cons)==4 and sum(c['credits'] for c in cons)==12
    ece=[c for c in data['courses'] if c['program_key']=='Early Childhood Education | Certificate of Achievement']
    assert len(ece)==10 and sum(c['credits'] for c in ece)==28
    assert all('MATH118/119'!=c['course_code'] for c in data['courses'])
if __name__=='__main__':
    data=build();validate(data)
    (HERE/'sipi-import-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    counts=collections.Counter(c['program_key'] for c in data['courses'])
    print(json.dumps({'programs':len(data['programs']),'courses':len(data['courses']),'held_course_rows':len(data['held_course_rows']),'course_counts':counts},indent=2))
