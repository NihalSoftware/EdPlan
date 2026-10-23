"""Import only page-cited IAIA catalog rows; dry-run by default.
Uses the existing EdPlan DATABASE_URL internally and never prints credentials.
"""
import argparse,collections,hashlib,json,pathlib,sys,uuid
from decimal import Decimal
from dotenv import dotenv_values
import psycopg2
from psycopg2.extras import Json,RealDictCursor,execute_values

HERE=pathlib.Path(__file__).resolve().parent
def validate(data):
    assert data['source']['catalog_year']=='2025-2026'
    assert len(data['programs'])==28
    keys={p['program_name']+' | '+p['degree'] for p in data['programs']}
    assert len(keys)==len(data['programs'])
    seen=set()
    for course in data['courses']:
        assert course['program_key'] in keys
        assert course['credits']>0 and course['credits']<=12
        assert course['course_name'].strip()
        assert course['recommended_year'] is None and course['recommended_semester'] is None
        key=(course['program_key'],course['course_code'])
        assert key not in seen
        seen.add(key)
        meta=course['metadata_json']
        assert 1<=meta['source_pdf_page']<=95
        assert meta['source_printed_page']==meta['source_pdf_page']+109
        assert float(meta['source_credit_row'].rstrip('*'))==course['credits']
    anchors={
      ('Cinematic Arts and Technology | Bachelor of Fine Arts','CINE105'):3,
      ('Computer Science | Bachelor of Science','CSAT202'):3,
      ('Business and Entrepreneurship | Certificate','BUSN120'):3
    }
    indexed={(c['program_key'],c['course_code']):c for c in data['courses']}
    for key,credits in anchors.items():assert indexed[key]['credits']==credits
    assert not any(p['program_name']=='Creative Writing' and p['degree']=='Minor' for p in data['programs'])
    assert not data['source']['is_current_catalog']
def fingerprint(cur,university_id):
    queries={
      'universities':("SELECT u.university_id AS id,to_jsonb(u)::text AS row FROM public.universities u WHERE u.university_id<>%s",),
      'programs':("SELECT p.program_id AS id,to_jsonb(p)::text AS row FROM public.programs p WHERE p.university_id<>%s",),
      'courses':("SELECT c.course_id AS id,to_jsonb(c)::text AS row FROM public.courses c JOIN public.programs p USING(program_id) WHERE p.university_id<>%s",)
    }
    result={}
    for table,(query,) in queries.items():
        cur.execute("SELECT count(*),md5(COALESCE(string_agg(md5(row),'' ORDER BY id),'')) FROM ("+query+") snapshot",(university_id,))
        result[table]=cur.fetchone()
    return result
def run():
    parser=argparse.ArgumentParser()
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--env-file',default='D:/EdPlan/fastapi_backend/.env')
    args=parser.parse_args()
    data=json.loads((HERE/'iaia-import-data.json').read_text(encoding='utf-8'))
    validate(data)
    conn=None
    try:
        url=dotenv_values(args.env_file).get('DATABASE_URL')
        if not url:raise RuntimeError('No configured database')
        conn=psycopg2.connect(url.replace('postgresql+asyncpg://','postgresql://',1),connect_timeout=10)
        conn.set_session(isolation_level='SERIALIZABLE')
        cur=conn.cursor()
        cur.execute('SET LOCAL lock_timeout = \'10s\'')
        cur.execute('SET LOCAL statement_timeout = \'60s\'')
        cur.execute("SELECT current_database()")
        if cur.fetchone()[0]!='edplan_db':raise RuntimeError('Unexpected database identity')
        cur.execute("SELECT pg_advisory_xact_lock(hashtext('IAIA-catalog-import'))")
        institution=data['institution']
        cur.execute("SELECT university_id FROM public.universities WHERE university_name=%s AND city=%s AND state=%s FOR UPDATE",(institution['university_name'],institution['city'],institution['state']))
        rows=cur.fetchall()
        if len(rows)!=1:raise RuntimeError('Expected exactly one existing IAIA college record')
        university_id=str(rows[0][0])
        before=fingerprint(cur,university_id)
        backup_path=HERE/'iaia-before-import.json'
        with conn.cursor(cursor_factory=RealDictCursor) as backup_cur:
            backup_cur.execute("SELECT * FROM public.universities WHERE university_id=%s",(university_id,))
            backup={'universities':backup_cur.fetchall()}
            backup_cur.execute("SELECT * FROM public.programs WHERE university_id=%s",(university_id,))
            backup['programs']=backup_cur.fetchall()
            backup_cur.execute("SELECT c.* FROM public.courses c JOIN public.programs p USING(program_id) WHERE p.university_id=%s",(university_id,))
            backup['courses']=backup_cur.fetchall()
        if not backup_path.exists():backup_path.write_text(json.dumps(backup,default=str,ensure_ascii=False,indent=2),encoding='utf-8')
        source_id='iaia-2526-'+data['source']['sha256'][:12]
        inserted_programs=[];inserted_courses=[];program_ids={}
        for program in data['programs']:
            key=program['program_name']+' | '+program['degree']
            metadata={**program['metadata_json'],'degree':program['degree'],'program':program['program_name'],'catalog_year':'2025-2026','catalog_source':data['source']['filename'],'catalog_title':'IAIA 2025-2026 College Catalog (provided excerpt)','source_sha256':data['source']['sha256'],'source_pdf_pages':program['source_pdf_pages'],'source_printed_pages':program['source_printed_pages'],'source_requirements_text':program['source_requirements_text'],'total_credit_hours':program['total_credit_hours'],'is_current_catalog':False,'course_import_is_partial':True,'catalog_import_id':source_id}
            cur.execute("INSERT INTO public.programs (university_id,program_name,degree,total_credit_hours,metadata_json,official_source_id,source_retrieved_at) VALUES (%s,%s,%s,%s,%s,%s,now()) ON CONFLICT (university_id,program_name,degree) DO NOTHING RETURNING program_id",(university_id,program['program_name'],program['degree'],program['total_credit_hours'],Json(metadata),source_id+':'+uuid.uuid5(uuid.NAMESPACE_URL,key).hex[:12]))
            row=cur.fetchone()
            if row:pid=str(row[0]);inserted_programs.append(pid)
            else:
                cur.execute("SELECT program_id,total_credit_hours,metadata_json FROM public.programs WHERE university_id=%s AND program_name=%s AND degree=%s",(university_id,program['program_name'],program['degree']))
                existing=cur.fetchone()
                if existing[1]!=program['total_credit_hours'] or (existing[2] or {}).get('catalog_import_id')!=source_id:raise RuntimeError('Existing program conflicts with this source; refusing to overwrite')
                pid=str(existing[0])
            program_ids[key]=pid
        cur.execute("SELECT program_id,course_id,course_code,credits,course_name FROM public.courses WHERE program_id=ANY(%s::uuid[])",(list(program_ids.values()),))
        existing_by_key=collections.defaultdict(list)
        for row in cur.fetchall():
            existing_by_key[(str(row[0]),row[2])].append((row[1],row[3],row[4]))
        pending=[]
        for course in data['courses']:
            pid=program_ids[course['program_key']]
            existing=existing_by_key.get((pid,course['course_code']),[])
            if existing:
                if len(existing)!=1 or Decimal(str(course['credits']))!=existing[0][1] or course['course_name']!=existing[0][2]:
                    raise RuntimeError('Existing course conflicts; refusing to overwrite')
                continue
            metadata={**course['metadata_json'],'catalog_import_id':source_id,'source_sha256':data['source']['sha256'],'course_import_is_partial':True}
            course_id=str(uuid.uuid4())
            pending.append((course_id,pid,course['course_code'],course['course_name'],course['credits'],Json(metadata),course['source_sequence'],source_id+':'+uuid.uuid5(uuid.NAMESPACE_URL,course['program_key']+':'+course['course_code']).hex[:12]))
            inserted_courses.append(course_id)
        if pending:
            execute_values(cur,"INSERT INTO public.courses (course_id,program_id,course_code,course_name,credits,metadata_json,source_sequence,official_source_id,source_retrieved_at) VALUES %s",pending,template="(%s,%s,%s,%s,%s,%s,%s,%s,now())",page_size=500)
        profile={'catalog_year':'2025-2026','source_filename':data['source']['filename'],'source_sha256':data['source']['sha256'],'is_current_catalog':False,'source_pdf_pages':95,'source_printed_page_range':[110,204],'program_count':len(data['programs']),'course_row_count':len(data['courses']),'held_course_row_count':len(data['held_course_rows']),'course_import_is_partial':True}
        cur.execute("UPDATE public.universities SET college_profile=COALESCE(college_profile,'{}'::jsonb)||jsonb_build_object('iaia_catalog_import',%s::jsonb) WHERE university_id=%s",(Json(profile),university_id))
        cur.execute("SELECT count(*) FROM public.programs WHERE university_id=%s",(university_id,))
        assert cur.fetchone()[0]==len(data['programs'])
        cur.execute("SELECT count(*) FROM public.courses c JOIN public.programs p USING(program_id) WHERE p.university_id=%s",(university_id,))
        assert cur.fetchone()[0]==len(data['courses'])
        assert fingerprint(cur,university_id)==before,'Other college catalog records changed'
        result={'mode':'applied' if args.apply else 'dry-run-rolled-back','database':'edplan_db','university_id':university_id,'program_count':len(data['programs']),'course_row_count':len(data['courses']),'inserted_program_ids':inserted_programs,'inserted_course_ids':inserted_courses,'other_colleges_unchanged':True,'source_sha256':data['source']['sha256']}
        if args.apply:conn.commit()
        else:conn.rollback()
        (HERE/('applied.json' if args.apply else 'dry-run.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in result.items() if not k.endswith('_ids')},indent=2))
        print('New program rows:',len(inserted_programs),'New course rows:',len(inserted_courses))
    except Exception as error:
        if conn:conn.rollback()
        print('Import rolled back:',type(error).__name__,getattr(error,'pgcode',None))
        raise SystemExit(1) from None
    finally:
        if conn:conn.close()
if __name__=='__main__':run()
