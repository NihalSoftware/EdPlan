"""Build page-cited NMMI degree metadata from preserved OCR and visually verified regions.
Course references have no credit values in this excerpt and are never course rows.
"""
import json,pathlib,re
HERE=pathlib.Path(__file__).resolve().parent

def region_text(region):
    page,col,start,end=region
    data=json.loads((HERE/'ocr'/f'page-{page:03}.json').read_text(encoding='utf-8-sig'))
    lines=[l for l in data['lines'] if start<=l['y']<end and (l['x']<710)==(col=='L')]
    rows=[]
    for line in sorted(lines,key=lambda l:(l['y'],l['x'])):
        if rows and abs(rows[-1]['y']-line['y'])<12:
            rows[-1]['parts'].append(line)
        else:rows.append({'y':line['y'],'parts':[line]})
    text='\n'.join(' '.join(l['text'] for l in sorted(row['parts'],key=lambda l:l['x'])) for row in rows)
    return {'source_pdf_page':page,'source_printed_page':page+18,'source_column':col,'source_y_range':[start,end],'source_text_ocr':text}

def build():
    config=json.loads((HERE/'extraction-config.json').read_text(encoding='utf-8'))
    data={'source':config['source'],'institution':config['institution'],'programs':[],'courses':[],
          'needs_clarification':config['needs_clarification'],
          'general_education':config['general_education'],'graduation_requirements':config['graduation_requirements']}
    shared=region_text([13,'R',920,1660])
    for spec in config['programs']:
        core=[region_text(r) for r in spec['core_regions']]
        concentrations=[]
        for name,regions in spec['concentrations']:
            sources=[region_text(r) for r in regions]
            concentrations.append({'name':name,'source_regions':sources,'is_separate_degree':False,
              'planning_ready':False,'course_credit_values_available':False,
              'source_pdf_pages':sorted({s['source_pdf_page'] for s in sources}),
              'source_printed_pages':sorted({s['source_printed_page'] for s in sources})})
        pages=sorted({13,*[s['source_pdf_page'] for s in core],*[n for c in concentrations for n in c['source_pdf_pages']]})
        meta={'abbreviation':spec['abbreviation'],'catalog_degree_heading':spec['program_name'],
              'total_credit_hours_is_minimum':True,'graduation_requirements':config['graduation_requirements'],
              'general_education':config['general_education'],'core_requirement_source_regions':core,
              'core_credit_requirements':[{'category':n,'minimum_credit_hours':low,**({'maximum_credit_hours':high} if low!=high else {})} for n,low,high in spec['core_credit_requirements']],
              'concentrations':concentrations,'concentrations_are_optional':True,
              'concentration_courses_may_also_satisfy_core':True,
              'planning_ready':False,'requires_catalog_course_details':True,
              'course_import_is_partial':True,'course_rows_imported':0,
              'course_credit_values_available':False,
              'import_limitation':'The provided excerpt lists course choices and category credits, not individual course credits. No course credit values or semester schedules are inferred.',
              'source_text_is_ocr':True,'source_text_review':'Degree titles, category totals, graduation minimums and concentration headings visually checked; source text retains OCR and source ambiguities.'}
        all_sources=[shared,*core,*[s for c in concentrations for s in c['source_regions']]]
        source_text='\n\n'.join(f"PDF page {s['source_pdf_page']} / printed {s['source_printed_page']}, column {s['source_column']}:\n{s['source_text_ocr']}" for s in all_sources)
        data['programs'].append({'program_name':spec['program_name'],'degree':spec['degree'],'total_credit_hours':spec['total_credit_hours'],
          'source_pdf_pages':pages,'source_printed_pages':[p+18 for p in pages],'source_requirements_text':source_text,'metadata_json':meta})
    return data

def validate(data):
    assert data['source']['catalog_year']=='2026-2027' and data['source']['pdf_page_count']==20
    assert data['source']['sha256']=='a3e1f115ca7318e3a9966147a3d6824689c59b6637eae4052420eaa32a56ac3e'
    assert len(data['programs'])==2 and data['courses']==[]
    assert [p['total_credit_hours'] for p in data['programs']]==[60,60]
    assert [len(p['metadata_json']['concentrations']) for p in data['programs']]==[10,9]
    assert sum(c[1] for c in data['general_education']['areas'])+data['general_education']['institutional_flex_credit_hours']==31
    for program in data['programs']:
        meta=program['metadata_json'];assert meta['total_credit_hours_is_minimum'] and not meta['planning_ready']
        assert meta['graduation_requirements']['minimum_institution_credit_hours']==24
        assert meta['graduation_requirements']['minimum_residence_semesters']==2
        assert all('maximum_credit_hours' not in r for r in meta['core_credit_requirements'] if r['category']!='Military Science/Leadership')
        for c in meta['concentrations']:
            assert not c['is_separate_degree'] and not c['course_credit_values_available']
            assert all(s['source_text_ocr'] for s in c['source_regions'])
        assert all(p+18==q for p,q in zip(program['source_pdf_pages'],program['source_printed_pages']))
    aa,as_=data['programs']
    assert next(x for x in aa['metadata_json']['core_credit_requirements'] if x['category']=='Laboratory Science')['minimum_credit_hours']==8
    assert next(x for x in as_['metadata_json']['core_credit_requirements'] if x['category']=='Laboratory Science')['minimum_credit_hours']==12
    assert 'more than the 60' in next(c for c in as_['metadata_json']['concentrations'] if c['name']=='Pre-Nursing')['source_regions'][0]['source_text_ocr']
    assert any('four required' in i['issue'] for i in data['needs_clarification'])

if __name__=='__main__':
    data=build();validate(data)
    (HERE/'nmmi-import-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Validated 2 programs, 19 concentrations, 0 credit-bearing course rows.')
